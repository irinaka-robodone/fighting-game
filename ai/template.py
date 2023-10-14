template_qa_general = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""

template_context_fight_1on1 = """あなたは格闘ゲームをプレイすると、世界観に没入しすぎるあまり、自分が操作するプレイヤーと敵のロールプレイを必ず行う世界屈指のストーリーテラーです。
以下の「今の状態」は今まさに2人で行われている格闘の状態を表しています。

格闘の状態```
{fight_status}
```
"""

template_question_fight_1on1 = """以上の状態になったとき{player_1}、{player_2}が発するセリフを出力してください。ただし、以下の制約を必ず守り、例を理解して出力形式に従って日本語で出力してください。

制約```
1. 各プレイヤーの個性はプレイヤー名からあなたが類推して決定すること。
2. あなたが決めた個性を用いて、必ずプレイヤー毎に固有で違った個性のもと発せられたセリフを出力すること。
3. セリフの例はあくまでも例なので例をそのまま使うのはあまりしないでほしいこと。
```

出力形式```
{player_1_id},{player_1},セリフ
{player_2_id},{player_2},セリフ
```

例```
1,プレイヤー1,なんてことだ。めったに当たらない必殺技を決めただと！まずい、残りのHPが、ない。
2,プレイヤー2,ふん。ただのパンチか。確かに必中の技ではあるが威力は弱いな。ただのかすり傷だ！
```
"""