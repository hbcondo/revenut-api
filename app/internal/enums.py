from enum import IntEnum

class RevenutChangeType(IntEnum):
	"""
	Enumeration describing how a metric changed over time
	"""
	
	INCREASE = 1
	DECREASE = -1
	NOCHANGE = 0

class RevenutAuthorizationType(IntEnum):
	"""
	Enumeration of how user performed authorization of account
	"""
	
	INITIALIZED = 0
	AUTHORIZED_CODE = 1
	AUTHORIZED_ID = 2
	REVOKED = -1
	ERROR = -2

def main() -> None:
	print(RevenutChangeType.INCREASE)
	print(RevenutAuthorizationType.AUTHORIZED_ID)

if __name__ == '__main__':
	main()