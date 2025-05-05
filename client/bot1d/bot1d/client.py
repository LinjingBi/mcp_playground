import json
import logging
from typing import Any
import os

from pydantic import BaseModel

from bot1d.llmx import LLMx
from bot1d.server import Server
from bot1d.config import format_tool_description, SHORT_MEMORY_DIR
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
    
    def load_short_memory(self) -> str | None:
        """
        List all conversation summary files in the short memory directory,
        sorted by modification time (newest first).
        Display file contents in groups of 5 files.
        """
        try:
            if not os.path.exists(SHORT_MEMORY_DIR):
                logging.info("No short memory directory found.")
                return
            
            files = os.listdir(SHORT_MEMORY_DIR)
            if not files:
                logging.info("No conversation summaries found.")
                return
                
            files.sort(key=lambda x: os.path.getmtime(os.path.join(SHORT_MEMORY_DIR, x)), reverse=True)
            
            for i in range(0, len(files), 5):
                group = files[i:i+5]
                logging.info(f"\n=== Group {i//5 + 1} of {(len(files)-1)//5 + 1} ===")
                file_dict = {}
                for index, file in enumerate(group):
                    try:
                        with open(os.path.join(SHORT_MEMORY_DIR, file), 'r') as f:
                            content = f.read()
                            file_dict[str(index)] = content
                            logging.info(f"\n{index}. {content}")
                    except Exception as e:
                        logging.error(f"Error reading file {file}: {e}")
                

                response = input("\nEnter number to select. Press Enter to see more files, or 'q' to quit: ").strip().lower()
                if response in file_dict:
                    return file_dict[response]
                elif response == 'q':
                    return None
                    
        except Exception as e:
            logging.error(f"Error loading short memory: {e}")
    
    async def talk(self):
        try:
            if not self._initialized:
                raise RuntimeError('Call initialize() first.')
            
            load_smemo = input("\nNeed recap?[yn]")
            if load_smemo.lower() == 'y':
                recap = self.load_short_memory()
                if recap:
                    self._prompt2llm + f"\n\nRecap: {recap}"
                
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
                        'content': new_msg,
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
                    logging.info('\nExiting...')
                    break
        finally:
            await self.cleanup()
