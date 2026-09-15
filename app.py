
from flask import Flask, jsonify, request
from src.desafio1_pipeline import processar_e_transformar_tarefas, calcular_estatisticas
app = Flask(__name__)

# Banco de dados em memória inicializado com o formato processado
tarefas_db = [
    {"id": 1, "titulo": "Configurar Repositório Git", "descricao": "Criar branches main, develop e Kanban", "concluida": True, "prioridade": "alta"},
    {"id": 2, "titulo": "Desenvolver Pipeline JSON", "descricao": "Implementar validações do Desafio 01", "concluida": True, "prioridade": "alta"},
    {"id": 3, "titulo": "Construir API Flask", "descricao": "Expor endpoints GET, POST, PUT, DELETE (Desafio 02)", "concluida": False, "prioridade": "media"}
]
proximo_id = 4


# --- TRATAMENTO GLOBAL DE ERROS ---
@app.errorhandler(404)
def recurso_nao_encontrado(e):
    return jsonify({"erro": "Recurso Não Encontrado", "mensagem": "O endpoint ou ID solicitado não existe."}), 404

@app.errorhandler(400)
def requisicao_invalida(e):
    return jsonify({"erro": "Requisição Inválida", "mensagem": "Dados incorretos ou campos obrigatórios ausentes."}), 400


# --- ROTAS RESTFUL (DESAFIO 02) ---

# 1. GET /tarefas (Com suporte a filtro e paginação)
@app.route('/tarefas', methods=['GET'])
def listar_tarefas():
    prioridade_filtro = request.args.get('prioridade')
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    
    resultado = tarefas_db.copy()
    
    if prioridade_filtro:
        resultado = [t for t in resultado if t["prioridade"] == prioridade_filtro.lower()]
        
    start = (page - 1) * limit
    end = start + limit
    
    return jsonify({
        "pagina": page,
        "limite": limit,
        "total_resultados": len(resultado),
        "dados": resultado[start:end]
    }), 200

# 2. GET /tarefas/<id>
@app.route('/tarefas/<int:tarefa_id>', methods=['GET'])
def obter_tarefa(tarefa_id):
    tarefa = next((t for t in tarefas_db if t["id"] == tarefa_id), None)
    if not tarefa:
        return jsonify({"erro": "Não Encontrado", "mensagem": f"A tarefa {tarefa_id} não existe."}), 404
    return jsonify(tarefa), 200

# 3. POST /tarefas (Usa o pipeline de validação e transformação do Desafio 01)
@app.route('/tarefas', methods=['POST'])
def criar_tarefa():
    global proximo_id
    dados = request.get_json()
    
    if not dados or "titulo" not in dados:
        return jsonify({"erro": "Dados Inválidos", "mensagem": "O campo 'titulo' é obrigatório."}), 400
        
    dados["id"] = proximo_id
    
    # Processa e transforma usando as funções do Desafio 01
    dados_processados = processar_e_transformar_tarefas([dados])
    
    if not dados_processados:
        return jsonify({"erro": "Falha de Processamento", "mensagem": "Payload JSON inválido."}), 400
        
    nova_tarefa = dados_processados[0]
    tarefas_db.append(nova_tarefa)
    proximo_id += 1
    
    return jsonify(nova_tarefa), 201

# 4. PUT /tarefas/<id>
@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
def atualizar_tarefa(tarefa_id):
    tarefa = next((t for t in tarefas_db if t["id"] == tarefa_id), None)
    if not tarefa:
        return jsonify({"erro": "Não Encontrado", "mensagem": f"A tarefa {tarefa_id} não existe."}), 404
        
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados Ausentes", "mensagem": "O corpo da requisição é obrigatório."}), 400
        
    tarefa["titulo"] = dados.get("titulo", tarefa["titulo"]).strip()
    tarefa["descricao"] = dados.get("descricao", tarefa["descricao"]).strip()
    tarefa["concluida"] = dados.get("concluida", tarefa["concluida"])
    tarefa["prioridade"] = dados.get("prioridade", tarefa["prioridade"]).lower()
    
    return jsonify(tarefa), 200

# 5. DELETE /tarefas/<id>
@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
def deletar_tarefa(tarefa_id):
    global tarefas_db
    tarefa = next((t for t in tarefas_db if t["id"] == tarefa_id), None)
    if not tarefa:
        return jsonify({"erro": "Não Encontrado", "mensagem": f"A tarefa {tarefa_id} não existe."}), 404
        
    tarefas_db = [t for t in tarefas_db if t["id"] != tarefa_id]
    return '', 204

# Endpoints Bônus: Estatísticas consolidadas (Calculadas pelo Desafio 01)
@app.route('/tarefas/estatisticas', methods=['GET'])
def obter_estatisticas():
    stats = calcular_estatisticas(tarefas_db)
    return jsonify(stats), 200

if __name__ == '__main__':
    app.run(debug=True)