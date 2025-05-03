import json
import logging
from typing import Any

from pydantic import BaseModel

from bot1d.llmx import LLMx
from bot1d.server import Server
from bot1d.config import format_tool_description
logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

class LLMTool(BaseModel):
    server: str
    tool: str
    arguments: dict[str, Any] | None

class BotClient:
    """
    1. initialize the connection with servers
    2. send the input to LLM
    3. get the response from LLM
    4. if LLM needs tool, send the tool call to server
    5. get the tool response from server
    6. send the tool response to LLM
    7. get the final answer from LLM
    """
    def __init__(self, llm: LLMx, servers: list[Server]) -> None:
        self.llm = llm
        self.servers = {ser.name: ser for ser in servers}
        self.tools_description = ''
        self._initialized = False
        self._prompt2llm = (
                "You are a helpful assistant with access to these extra tools:\n\n"
                "{tools_description}\n"
                "Choose the appropriate tool based on the user's question. "
                "If no tool is needed, reply directly.\n\n"
                "IMPORTANT: When you need to use tools, you must ONLY respond with "
                "the exact JSON object format below, nothing else:\n"
                '{{"mcptools":[{{\n'
                '    "server": "server-name",\n'
                '    "tool": "tool-name",\n'
                '    "arguments": {{\n'
                '        "argument-name": "value"\n'
                "    }}\n"
                "}}]}}\n\n"
                "After receiving a tool's response:\n"
                "1. Transform the raw data into a natural, conversational response\n"
                "2. Keep responses concise but informative\n"
                "3. Focus on the most relevant information\n"
                "4. Use appropriate context from the user's question\n"
                "5. Avoid simply repeating the raw data\n\n"
                "Please use only the tools that are explicitly defined above."
            )
    async def cleanup(self):
        try:
            await self.llm.cleanup()
            for server in self.servers.values():
                await server.cleanup()
        except Exception as err:
            logging.warning(f"Warning during final cleanup: {err}")


    async def initialize(self):
        for server in self.servers.values():
            await server.initialize()
            tools = await server.list_tools()
            descrip = format_tool_description(server.name, tools)
            self.tools_description += descrip + '\n'
        self._prompt2llm = self._prompt2llm.format(
            tools_description=self.tools_description if self.tools_description else 'No Tool Available.')
        self._initialized = True

    async def handle_llm_response(self, rsp: str) -> str:
        try:
            rsp_json = json.loads(rsp)
        except json.JSONDecodeError:
            return rsp
        
        results = {}
        if 'mcptools' in rsp_json:
            for tool in rsp_json['mcptools']:
                llm_tool = LLMTool(**tool)
                if llm_tool.server not in self.servers:
                    raise ValueError(f'LLM requested an unknown server: {llm_tool.server}. Availables: {self.servers.keys()}')
                mcp_server = self.servers[llm_tool.server]
                tool_rsp = await mcp_server.call_tool(llm_tool.tool, llm_tool.arguments)
                results[llm_tool.server] = tool_rsp
            return str(results)
        else:
            return rsp
    
    async def talk(self):
        try:
            if not self._initialized:
                raise RuntimeError('Call initialize() first.')

            messages = [{
                'role': "system",
                'content': self._prompt2llm
            }]
            logging.info(f'\nsystem: {self._prompt2llm}')

            while True:
                try:
                    new_msg = input('You:').strip()
                    if new_msg.lower() in ["quit", "exit"]:
                        logging.info("\nExiting...")
                        break
                    messages.append({
                        'role': 'user',
                        'content': new_msg
                    })
                    
                    llm_answer = await self.llm.chat(messages)
                    logging.info(f'\nassistant: {llm_answer}')
                    messages.append({
                            'role': 'assistant',
                            'content': llm_answer,
                        })
                    
                    processed_llm_answer = await self.handle_llm_response(llm_answer)
                    if llm_answer != processed_llm_answer:
                        logging.info(f'\nsystem: {processed_llm_answer}')
                        messages.append({
                            'role': 'system',
                            'content': processed_llm_answer,
                        })
                        
                        final_llm_answer = await self.llm.chat(messages)
                        logging.info(f'\nassistant: {final_llm_answer}')
                        messages.append({
                            'role': 'assistant',
                            'content': final_llm_answer,
                        })
                except KeyboardInterrupt:
                    logging.info('exiting...')
                    break
        finally:
            await self.cleanup()
