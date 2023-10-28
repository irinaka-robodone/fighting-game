import os
import csv
import io
import pandas as pd
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI

from . import template
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_script(data: pd.DataFrame, model_name: str = "gpt-4", temperature: float = 0.3, max_tokens: int = 500, max_retries: int = 2):
    """
    # ゲームの進行状態を参考に、自然言語モデルからNPC、プレイヤーのセリフを出力させる関数
    
    ## todo
    1. ゲームの進行状態を表す抽象データ構造をつくる。
    1. このデータ構造に従ったデータとプロンプトテンプレートをもとに自然言語モデルに与えるプロンプトをつくる。
    1. プロンプトを自然言語モデルのAPIに与えて、モデルの出力を関数の返り値にする。
    """
    df = data
    player_1_name = df[df["Status Name"] == "プレイヤー1_名前"].values[0][1]
    player_2_name = df[df["Status Name"] == "プレイヤー2_名前"].values[0][1]
    player_1_id = df[df["Status Name"] == "player_1_id"].values[0][1]
    player_2_id = df[df["Status Name"] == "player_2_id"].values[0][1]
    
    print(player_1_name, player_2_name)
    
    game_status = df.to_markdown(None, mode="w", index=None)
    
    qa_template = template.template_qa_general
    context = template.template_context_fight_1on1.format(fight_status=game_status)
    question = template.template_question_fight_1on1.format(player_1_id = player_1_id, player_2_id = player_2_id, player_1=player_1_name, player_2=player_2_name)
    
    llm = ChatOpenAI(model_name = model_name, temperature=0.0, max_tokens=max_tokens, max_retries=max_retries, request_timeout=30)
    
    qa_prompt = PromptTemplate(
        template=qa_template, input_variables=["context", "question"]
    )
    qa_chain = LLMChain(
        llm=llm,
        prompt=qa_prompt
    )
    try:
        res = qa_chain.run({"context": context, "question": question})
        f = io.StringIO()
        f.write(res)
        f.seek(0)
        # csvモジュールで読み出し
        csv_reader = csv.reader(f, delimiter=",")
        res = [row for row in csv_reader]
        
        df = pd.DataFrame(res, columns=["player_id","player_name", "response"], index=None)
        df = df.astype(str)
        df["player_id"] = df["player_id"].str.strip()
        
        player_1_res = df[df["player_id"] == "1"].values[0][2]
        player_2_res = df[df["player_id"] == "2"].values[0][2]
        
        ret = [player_1_res, player_2_res]
        print(f"{player_1_name}: {player_1_res}")
        print(f"{player_2_name}: {player_2_res}")
    except:
        ret = ["", ""]
    
    return ret
    
if __name__ == "__main__":
    data = [["Status Name", "Description"], ["player_1_id", "1"], ["player_2_id", "2"], ["プレイヤー1_名前", "ペンシルヘッド"], ["プレイヤー2_名前", "ファイヤーロボ"], ["技を受ける前のプレイヤー1のHP", "90"], ["技を受ける前のプレイヤー2のHP", "70"], ["プレイヤー1の出した技", "必殺技。成功確率は30%と必中ではないが、当たると60ダメージを与えられる。"], ["プレイヤー2の出した技", "パンチ。成功確率100%。必中の技で10ダメージを与えられる。"], ["プレイヤー1の出した技の結果", "成功"], ["プレイヤー2の出した技の結果", "成功"]]
    df = pd.DataFrame(data[1:], index=None, columns=data[0])
    ret = get_script(df, temperature=0.5)
    
    print(ret)
