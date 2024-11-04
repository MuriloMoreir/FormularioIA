from flask import Flask, render_template, request
import pickle as pkl
import pandas as pd
import requests
import urllib3

app = Flask(__name__)

# Desserialização do preprocessador
preprocessador_caminho = 'preprocessador.pkl'

with open(preprocessador_caminho, 'rb') as file:
    preprocessador_desserializado = pkl.load(file)

# Desserialização do model
model_caminho = 'model.pkl'

with open(model_caminho, 'rb') as file:
    model_desserializado = pkl.load(file)

# <-- FIM DESSERIALIZAÇÃO -->

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":

        # Obter as respostas do formulário
        respostas = {
            "nome": request.form.get("nome"),
            "email": request.form.get("email"),
            "faixa_etaria": request.form.get("faixa_etaria"),
            "renda_familiar": request.form.get("renda_familiar"),
            "pratica_sustentavel": request.form.get("pratica_sustentavel"),
            "frequencia_sustentavel": request.form.get("frequencia_sustentavel") if request.form.get("pratica_sustentavel") == "Sim" else None,
            "aprendeu_sustentabilidade": request.form.get("aprendeu_sustentabilidade"),
            "incluiu_jogos": request.form.get("incluiu_jogos") if request.form.get("aprendeu_sustentabilidade") == "Sim" else None,
            "jogos_para_aprendizado": request.form.get("jogos_para_aprendizado"),
            "consome_aplicativos": request.form.get("consome_aplicativos"),
            "conhecimento_importante": request.form.get("conhecimento_importante"),

            # Capturando cada funcionalidade como True ou False
            "jogos_aprendizado": bool(request.form.get("jogos_aprendizado")),
            "atividades_praticas": bool(request.form.get("atividades_praticas")),
            "quizzes_conhecimento": bool(request.form.get("quizzes_conhecimento")),
            "videos_profissionais": bool(request.form.get("videos_profissionais")),
        }

        # Criar DataFrame com as respostas (exceto 'nome' e 'email')
        df_respostas = pd.DataFrame([{
            'Qual sua faixa etária ?': respostas["faixa_etaria"],
            'Qual é a sua renda familiar mensal, considerando as seguintes faixas:': respostas['renda_familiar'],
            'Você adota alguma\xa0prática sustentável\xa0(ações que visam a utilização eficiente dos recursos naturais, sem os esgotar ou prejudicar os ecossistemas)\xa0no seu dia a dia?': respostas['pratica_sustentavel'],
            'Com que frequência você pratica uma ação sustentável ?': respostas['frequencia_sustentavel'],
            'Você aprendeu ou teve aulas sobre\xa0sustentabilidade\xa0na escola?': respostas['aprendeu_sustentabilidade'],
            'Se você aprendeu sustentabilidade na escola, inclui-a jogos para a sua aprendizagem?': respostas['incluiu_jogos'],
            'Você acredita que jogos podem ajudar no aprendizado sobre sustentabilidade?\n': respostas['jogos_para_aprendizado'],
            'Você faz ou já fez o consumo de outros aplicativos / plataformas de sustentabilidade e ESG (Governança ambiental, social e corporativa) ?': respostas['consome_aplicativos'],
            'Você acha que o conhecimento sobre Sustentabilidade / ESG (Governança ambiental, social e corporativa) é crucial para o seu desenvolvimento profissional ?': respostas['conhecimento_importante'],
            'Jogos para seu aprendizado': respostas['jogos_aprendizado'],
            'Atividades práticas para seu desenvolvimento': respostas['atividades_praticas'],
            'Quizzes para testar seu conhecimento': respostas['quizzes_conhecimento'],
            'Vídeos com profissionais falando sobre Sustentabilidade e ESG': respostas['videos_profissionais'],
        }])

        print("----------------------------------------------------------------------")

        novas_entradas = preprocessador_desserializado.transform(df_respostas)
        
        # Previsão do modelo usando o DataFrame
        previsao = model_desserializado.predict(novas_entradas)[0]

        if previsao == 0:
            previsao_texto = 'Estudantil'
            previsao = f'A IA preveu que sua motivação será: {previsao_texto}'
        else:
            previsao_texto = 'Não tenho motivação'
            previsao = f'A IA preveu que sua motivação será: {previsao_texto}'

        # <-- Chamando API para armazenar no MongoDB-->

        url = "https://gats-educaeco-api-mongodb.onrender.com/api/resultados/adicionar"
        dados = {
            "nome": respostas["nome"],
            "email": respostas["email"],
            "resultado": previsao_texto
        }

        urllib3.disable_warnings()

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=dados, headers=headers, verify=False)

        if response.status_code == 200:  # Sucesso de criação
            print("Requisição bem-sucedida:", response.json())
        else:
            print(f"Erro: {response.status_code}")
            print("Detalhes do erro:", response.text)

        # Renderizar resultado
        return render_template("result.html", nome=respostas["nome"], predicao=previsao)
    return render_template("form.html")

if __name__ == "__main__":
   app.run(debug=True, port = 5000, host = '0.0.0.0')
