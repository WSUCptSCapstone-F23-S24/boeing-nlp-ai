import openai
import gradio

client = openai.OpenAI(
    api_key="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",
)

messages = [{"role": "system", "content": "You are a Boeing Executive that knows all about the company"}]

def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
    ChatGPT_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

demo = gradio.Interface(fn=CustomChatGPT, inputs = "text", outputs = "text", title = "BoeingAI")

demo.launch(share=True)