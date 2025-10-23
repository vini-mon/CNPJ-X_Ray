# Aqui temos os dois agentes comentados no projeto.

# Cadastral_agent é o agente principal que faz a análise do CNPJ.
# Risk_analysis_agent é responsável por aplicar as regras de negócio e classificar o risco para um CNPJ.

# Em trabalhos futuros, destrinchar os agentes em arquivos separados pode ser interessante para organização. Por ora, deixo tudo aqui para facilitar a visualização.

import httpx
from datetime import datetime		# Para manipulação de datas (data de abertura do CNPJ)

from .schemas import Cnpj_input_data, Analysis_output_data

# Agente responsável por obter e analisar os dados cadastrais de um CNPJ
class Cadastral_agent:

	API_URL_Base = "https://open.cnpja.com/office"	# URL base da API CNPJá

	# Buscar os dados do CNPJ na API CNPJá
	def get_cnpj_data(self, cnpj: str) -> Cnpj_input_data:

		url = f"{self.API_URL_Base}/{cnpj}"

		try:

			with httpx.Client(timeout = 10.0) as client:

				response = client.get(url)

				# Trata erros de HTTP
				response.raise_for_status()

				# Valida e retorna os dados usando o schema definido
				data = response.json()
				cnpj_data = Cnpj_input_data(**data)
				return cnpj_data
			
		except httpx.HTTPStatusError as e:

			print(f"[Cadastral_agent]: Erro #00 - busca do CNPJ: {cnpj}")
			print(f"***\n{e}\n***")
			raise ConnectionError("Não foi possível encontrar os dados.")
		
		except httpx.RequestError as e:

			print(f"[Cadastral_agent]: Erro #01 - Erro de conexão")
			print(f"***\n{e}\n***")
			raise ConnectionError("Erro de conexão com a API.")

		except Exception as e:

			print(f"[Cadastral_agent]: Erro #02 - Erro inesperado!")
			print(f"***\n{e}\n***")
			raise

# Agente responsável por analisar o risco de um CNPJ com base em regras de negócio
class Risk_analysis_agent:

	# As constantes da análise do negócio
	MIN_CAPITAL_APROVADO = 100000.0		# Capital social mínimo para aprovação
	MIN_CAPITAL_ALERTA = 50000.0 		# Capital social mínimo para risco moderado
	MIN_TEMPO_APROVADO = 2				# Tempo mínimo de abertura em anos para aprovação
	MIN_TEMPO_ALERTA = 1				# Tempo mínimo de abertura em anos para risco moderado
	CNAE_EDUCACAO_PREFIXO = "85"		# Prefixo CNAE relacionado a educação

	POSITIVE_POINTS = 1					# Pontos positivos na análise
	ALERT_POINTS = -2					# Pontos de alerta na análise
	NEGATIVE_POINTS = -10				# Pontos negativos na análise

	# Executa a análise de risco com base nos dados do CNPJ
	def analyze(self, cnpj: str, data: Cnpj_input_data) -> Analysis_output_data:

		justificativas = []
		score = 0

		# Critário 1: Capital Social
		if data.status.text.upper() == "ATIVA":

			score += self.POSITIVE_POINTS

		else: 

			score += self.NEGATIVE_POINTS
			justificativas.append(f"CNPJ não ATIVO Status: {data.status.text}.")

		# Critério 2: Capital Social

		capital_social = data.company.equity
		if capital_social is not None:

			if capital_social >= self.MIN_CAPITAL_APROVADO:

				score += self.POSITIVE_POINTS

			elif capital_social >= self.MIN_CAPITAL_ALERTA:

				score += self.ALERT_POINTS
				justificativas.append(f"Capital Social abaixo do ideal: R$ {capital_social:.2f}. Critério ideal é R$ {self.MIN_CAPITAL_APROVADO:.2f}.")

			else:

				score += self.NEGATIVE_POINTS
				justificativas.append(f"Capital Social muito baixo: R$ {capital_social:.2f}. Critério mínimo é R$ {self.MIN_CAPITAL_ALERTA:.2f}.")

		else:

			score += self.ALERT_POINTS
			justificativas.append("Capital Social não informado ou nulo.")

		# Critério 3: Tempo de Abertura
		if data.founded is not None:

			try:

				opening_date = datetime.strptime(data.founded, "%Y-%m-%d").date()
				today = datetime.now().date()
				operating_time = (today - opening_date).days / 365.25

				if operating_time >= self.MIN_TEMPO_APROVADO:

					score += self.POSITIVE_POINTS

				elif operating_time >= self.MIN_TEMPO_ALERTA:

					score += self.ALERT_POINTS
					justificativas.append(f"Tempo de abertura abaixo do ideal: {operating_time:.2f} anos. Critério ideal é {self.MIN_TEMPO_APROVADO:.2f} anos.")

				elif operating_time < self.MIN_TEMPO_ALERTA:

					score += self.NEGATIVE_POINTS
					justificativas.append(f"Tempo de abertura muito baixo: {operating_time:.2f} anos. Critério mínimo é {self.MIN_TEMPO_ALERTA:.2f} anos.")

			except ValueError as e:

				score += self.ALERT_POINTS
				justificativas.append(f"Data de abertura inválida: {e}.")

		else:

			score += self.ALERT_POINTS
			justificativas.append("Data de abertura não informada.")

		# Critério 4: CNAE Principal
		main_cnae_education = str(data.main_cnae.id).startswith(self.CNAE_EDUCACAO_PREFIXO)
		side_cnae_education = False

		if data.secondary_cnaes:

			# Encontrar pelo menos um CNAE secundário relacionado à educação
			for cnae in data.secondary_cnaes:

				if str(cnae.id).startswith(self.CNAE_EDUCACAO_PREFIXO):
					side_cnae_education = True
					break

		if main_cnae_education:

			score += self.POSITIVE_POINTS

		elif side_cnae_education:

			score += self.ALERT_POINTS
			justificativas.append("CNAE principal não relacionado à educação, mas há CNAE secundário relacionado.")
	
		else:

			score += self.NEGATIVE_POINTS
			justificativas.append("Nenhum CNAE relacionado à educação encontrado.")

		if score < 0:
			classificacao = "Reprovado"

		elif 0 <= score <= 2:
			classificacao = "Atenção"

		else:
			classificacao = "Aprovado"

		# Monta o output final da análise
		return Analysis_output_data(

			cnpj = cnpj,
			razao_social = data.company.name,
			classificacao = classificacao,
			score = score,
			justificativas = justificativas,
			# dados_brutos = data.model_dump()

		)