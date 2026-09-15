
def validar_payload_json(dados):
    """Valida a estrutura do payload de entrada."""
    if not isinstance(dados, list):
        raise ValueError("O payload JSON de entrada deve ser uma lista (array) de objetos.")
    return True

def processar_e_transformar_tarefas(dados_brutos):
    """
    Aplica regras de negócio usando métodos de array/listas e loops.
    Filtra tarefas válidas, limpa dados e calcula campos formatados.
    """
    validar_payload_json(dados_brutos)
    
    tarefas_processadas = []
    for item in dados_brutos:
        if not isinstance(item, dict):
            continue
            
        id_item = item.get("id")
        titulo = str(item.get("titulo", "")).strip()
        descricao = str(item.get("descricao", "")).strip()
        concluida = bool(item.get("concluida", False))
        prioridade = str(item.get("prioridade", "media")).lower()
        
        # Ignora itens sem ID ou Título válido
        if not id_item or not titulo:
            continue
            
        tarefas_processadas.append({
            "id": int(id_item),
            "titulo": titulo,
            "descricao": descricao,
            "concluida": concluida,
            "prioridade": prioridade if prioridade in ["alta", "media", "baixa"] else "media"
        })
        
    return tarefas_processadas

def calcular_estatisticas(tarefas):
    """Retorna métricas consolidadas sobre o conjunto de dados."""
    total = len(tarefas)
    concluidas = sum(1 for t in tarefas if t["concluida"])
    pendentes = total - concluidas
    
    return {
        "total_tarefas": total,
        "concluidas": concluidas,
        "pendentes": pendentes,
        "taxa_conclusao_pct": round((concluidas / total * 100), 2) if total > 0 else 0.0
    }