# Código da aplicação Eel para interface web

import eel
import sys
import json

try:
	from main import Orchestrator_agent

except ImportError as e:

	print(f"[app]: Erro #01 ao importar Orchestrator_agent: {e}", file=sys.stderr)
	sys.exit(1)

# Pasta dos arquivos web (HTML, CSS, JS)
eel.init('web')

try:

	orchestrator = Orchestrator_agent()

except Exception as e:

	print(f"[app]: Erro #02 ao iniciar Orchestrator_agent: {e}", file=sys.stderr)
	sys.exit(1)

# Funções expostas para a interface web
@eel.expose

# Função para analisar a lista de CNPJ e retornar o resultado
def analyze_cnpj(cnpj_list):

	print(f"[App]: Recebido pedido da interface para processar {len(cnpj_list)} CNPJs.")

	if not cnpj_list:
		return {"status": "error", "message": "Lista de CNPJ vazia."}

	for cnpj in cnpj_list:

		if not cnpj.strip():

			continue

		# Tenta executar o processamento do CNPJ, capturando erros
		try:

			result_dict = orchestrator.run_analysis(cnpj)

			if not isinstance(result_dict, dict):

				result_dict = {
					"status": "error",
					"cnpj": cnpj,
					"message": "Falha interna: resultado inválido."
				}

		except Exception as e:

			result_dict = {
				"status": "error",
				"cnpj": cnpj,
				"message": f"Exceção durante a análise: {str(e)}"
			}
			
		# Envia o resultado de volta para a interface web
		eel.update_results_js(json.dumps(result_dict))

	print("[App]: Processamento da interface concluído.")
	eel.processing_complete_js()

# Ponto de entrada principal da aplicação Eel
if __name__ == "__main__":

	print("[App]: Iniciando a aplicação Eel para a interface web.")

	try:

		eel.start('index.html', size=(900, 800))

	except Exception as e:

		print(f"[app]: Erro #03 ao iniciar a interface web: {e}", file=sys.stderr)
		sys.exit(1)

	finally:
		print("[App]: Aplicação Eel encerrada.")