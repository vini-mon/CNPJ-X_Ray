# Este arquivo define os "contratos" de dados (schemas) da aplicação
# Isso garante a estruturados dados na hora da entrada e da saída.

from pydantic import BaseModel, Field	# BaseModel é a classe base para todos os schemas e Field é usado para definir campos com validações adicionais
from typing import List, Optional, Any	# List é para listas de itens e Optional um campo que pode nn existir, com isso evitamos erros

# Struct do status
class Status(BaseModel):

	id: int
	text: str

# Struct do CNAE
class Cnae(BaseModel):
 
	id: int
	text: str

# Sctruct da empresa com capital social
class Company(BaseModel):

	name: Optional[str] = None
	equity: Optional[float] = None  

# Aqui seto os campos de interesse que vou extrair da API
class Cnpj_input_data(BaseModel):

	status: Status
	company: Company
	founded: Optional[str] = None
	main_cnae: Cnae = Field(..., alias="mainActivity")
	secondary_cnaes: List[Cnae] = Field(default_factory=list, alias="sideActivities")

	class Config:
		extra = 'ignore'  # Ignorar campos extras não definidos no schema

# Aqui é o formato final da saída da análise
class Analysis_output_data(BaseModel):

	cnpj: str
	razao_social: Optional[str]
	classificacao: str
	score: int
	justificativas: List[str]
	dados_brutos: Optional[Any] = None  # Campo opcional para armazenar dados brutos


