from enum import StrEnum

class RevenutChangeType(StrEnum):
	"""
	Enumeration describing how a metric changed over time
	"""
	
	INCREASE = 'INCREASE'
	DECREASE = 'DECREASE'
	NOCHANGE = 'NOCHANGE'

class RevenutAuthorizationType(StrEnum):
	"""
	Enumeration of how user performed authorization of account
	"""
	
	INITIALIZED = "INITIALIZED"
	AUTHORIZED_CODE = "AUTHORIZED_CODE"
	AUTHORIZED_ID = "AUTHORIZED_ID"
	REVOKED = "REVOKED"

def main() -> None:
	print(RevenutChangeType.INCREASE)
	print(RevenutAuthorizationType.AUTHORIZED_ID)

if __name__ == '__main__':
	main()