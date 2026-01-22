from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver 

load_dotenv()

class ChatState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]

model = ChatGroq(
    model='openai/gpt-oss-120b',
    temperature=0.2
)

def chat_node(state: ChatState):
    # take your query from state
    query = state['message']

    # send to llm
    response = model.invoke(query)

    # response store into the state
    return {'message': [response]}

checkpointer = InMemorySaver()
graph = StateGraph(ChatState)

# add node
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)


thread_id = '1'
while True:
    usr_msg = input('Type here: ')
    print("User msg: ", usr_msg)

    if usr_msg.strip().lower() in ['exit', 'bye', 'quit']:
        print("AI: Thank You :)")
        break

    config = {'configurable': {'thread_id': thread_id}}

    response = chatbot.invoke({'message': [HumanMessage(content=usr_msg)]}, config=config)
    print('AI: ', response['message'][-1].content)

print(chatbot.get_state(config=config))