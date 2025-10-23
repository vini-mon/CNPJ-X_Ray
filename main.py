"""
Este é o script principal - O Agente Orquestrador como descrito no README.

Ele coordena o fluxo de trabalho para uma lista de CNPJs:

1) Recebe um ou mais CNPJs via linha de comando.
2) Para cada CNPJ, aciona o Agente Cadastral.
3) Aciona o Agente de Risco para analisar os dados.
4) Imprime o resultado final para cada CNPJ.

Como executar (via Linha de Comando):

	python main.py "45.954.282/0001-02"
	python main.py "45.954.282/0001-02" "19.131.243/0001-97" "99999999000191"

"""

import sys
import json
from pydantic import ValidationError

from tools.agents import Cadastral_agent, Risk_analysis_agent

# Limpa o CNPJ, removendo caracteres não numéricos
def clean_cnpj(cnpj: str) -> str:
	
	return "".join(filter(str.isdigit, cnpj))

# Agente Orquestrador que coordena os outros agentes
class Orchestrator_agent:

	# Inicializa os agentes cadastral e de risco
	def __init__(self):
		self.cadastral_agent = Cadastral_agent()
		self.risk_analysis_agent = Risk_analysis_agent()

	# Executa o fluxo completo de análise de ponta a ponta para cada CNPJ.
	# Retorna um dicionário com o resultado da análise.
	def run_analysis(self, dirt_cnpj: str):

		try:

			cnpj = clean_cnpj(dirt_cnpj)

			if(len(cnpj) != 14):

				print(f"[Orchestrator_agent]: Erro #01 - CNPJ inválido: {dirt_cnpj}", file = sys.stderr)	# file=sys.stderr para imprimir erros no stderr
				return {"status": "error", "cnpj": dirt_cnpj, "razao_social": None, "message": "CNPJ inválido."}

			# Começa a análise do CNPJ
			print(f"[Orchestrator_agent]: Iniciando análise para o CNPJ: {dirt_cnpj}\n")

			# Aciona o agente cadastral para obter os dados
			dados_cnpj = self.cadastral_agent.get_cnpj_data(cnpj)

			# Aciona o agente de risco para analisar os dados
			resultado_analise = self.risk_analysis_agent.analyze(cnpj, dados_cnpj)

			print(f"[Orchestrator_agent]: Resultado da análise para o CNPJ {dirt_cnpj}: {resultado_analise.model_dump_json(indent=4, ensure_ascii=False)}")
			return {"status": "success", "cnpj": dirt_cnpj, "razao_social": resultado_analise.razao_social, "data": resultado_analise.model_dump(mode = 'json')}
		
		# Tratamento de erros - Falhas
		except (ValueError, ConnectionError, ValidationError) as e:

			print(f"[Orchestrator_agent]: Erro #02 - Falha na análise do CNPJ: {dirt_cnpj}", file = sys.stderr)
			print(f"***\n{e}\n***", file = sys.stderr)

			return {"status": "error", "cnpj": dirt_cnpj, "razao_social": None, "message": str(e)}
		
		except Exception as e:

			print(f"[Orchestrator_agent]: Erro #03 - Erro inesperado na análise do CNPJ: {dirt_cnpj}", file = sys.stderr)
			print(f"***\n{e}\n***", file = sys.stderr)

			return {"status": "error", "cnpj": dirt_cnpj, "razao_social": None, "message": f"Erro inesperado. Detalhes: {str(e)}"}
		
# Ponto de entrada principal
if __name__ == "__main__":

	if len(sys.argv) < 2:

		print("Uso: python main.py \"<CNPJ1>\" \"<CNPJ2>\" ...", file = sys.stderr)
		sys.exit(1)

	# Pega a lista de CNPJs da linha de comando
	cnpj_list_input = sys.argv[1:]

	# Iniciando processamento
	print(f"[main]: Iniciando o Orquestrador para os {len(cnpj_list_input)} CNPJs fornecidos.")
	print(f"[main]: CNPJs recebidos: {cnpj_list_input}")

	orchestrator = Orchestrator_agent()

	success_count = 0
	failure_count = 0

	# Processa cada CNPJ individualmente
	for cnpj in cnpj_list_input:

		print(f"\n\n" + "-" * 40 + "\n\n")

		result = orchestrator.run_analysis(cnpj)

		if result["status"] == "success":

			success_count += 1
			print(f"[main]: Análise bem-sucedida para o CNPJ {cnpj}.")
			print(json.dumps(result['data'], indent=4, ensure_ascii=False))

		else:

			failure_count += 1
			print(f"[main]: Análise falhou para o CNPJ {cnpj}. Motivo: {result['message']}", file = sys.stderr)
			print(json.dumps(result, indent=4, ensure_ascii=False), file=sys.stderr)

		print(f"\n\n" + "-" * 40 + "\n\n")

	print(f"[main]: {success_count + failure_count} Análises concluídas.")
	print(f"\tSucessos: {success_count}")
	print(f"\tFalhas: {failure_count}.")