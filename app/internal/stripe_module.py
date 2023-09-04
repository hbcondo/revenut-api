from enums import RevenutChangeType, RevenutAuthorizationType
from dotenv import load_dotenv
from pydantic import BaseModel
from zoneinfo import ZoneInfo

import os
import calendar
import datetime
import dateutil.relativedelta
import locale
import logging
import time
import concurrent.futures

import stripe

load_dotenv()
stripe.api_key = os.getenv('STRIPE_API_KEY')
stripe.log = 'info'		

class RevenutStripe(BaseModel):
	#region Properties
	IsAuthorized:bool = False
	Status:RevenutAuthorizationType | None = None
	Code:int = 0
	Error:str | None = None
	AccountID:str | None = None
	AccountName:str | None = None
	AccountIconURL:str | None = None
	AuthorizationCode:str | None = None
	TimezonePreference:str | None = None
	DateToday:datetime.datetime = datetime.datetime.now()
	DateDayStartCurrent:datetime.datetime = datetime.datetime.now()
	DateDayEndCurrent:datetime.datetime = datetime.datetime.now()
	DateMonthStartCurrent:datetime.datetime = datetime.datetime.now()
	DateMonthEndCurrent:datetime.datetime = datetime.datetime.now()
	DateMonthEndPrevious:datetime.datetime = datetime.datetime.now()
	DateMonthToDateCurrent:datetime.datetime = datetime.datetime.now()
	DateMonthStartPrevious:datetime.datetime = datetime.datetime.now()
	DateMonthToDatePrevious:datetime.datetime = datetime.datetime.now()
	VolumeGrossToday:float = 0
	VolumeGrossMonthCurrent:float = 0
	VolumeGrossMonthCurrentPercent:float = 0
	VolumeGrossMonthPrevious:float = 0
	VolumeGrossMonthToDatePrevious:float = 0
	VolumeGrossMonthForecast:float = 0
	VolumeGrossMonthOverMonthPercentChangeType:RevenutChangeType = RevenutChangeType.NOCHANGE
	VolumeGrossMonthOverMonthPercentChange:float = 0
	VolumeGrossMonthToMonthPercentChange:float = 0
	VolumePending:float = 0
	VolumePendingPercent:float = 0
	VolumeTrialing:float = 0
	VolumeTrialingPercent:float = 0
	CountPaymentsToday:int = 0
	CountTrialingToday:int = 0
	CountTrialingMonthCurrent:int = 0
	#endregion

	def __init__(self, *a, **kw):
		super().__init__(*a, **kw)

		if (self.TimezonePreference):
			self.set_locale()
			self.Status = RevenutAuthorizationType.INITIALIZED

		if (self.AuthorizationCode):
			token = self.token(self.AuthorizationCode)

			if (isinstance(token, dict)):
				self.AccountID = self.user_id(token)
				self.Status = RevenutAuthorizationType.AUTHORIZED_CODE
				self.IsAuthorized = True
			elif (isinstance(token, stripe.error.StripeError)):
				self.Status = RevenutAuthorizationType.ERROR
				self.Error = token.user_message
				self.Code = token.http_status

		elif (self.AccountID):
			with concurrent.futures.ThreadPoolExecutor() as pool:
				transactions = pool.submit(self.transactions, self.AccountID, int(self.DateMonthStartPrevious.timestamp()))
				subscriptions = pool.submit(self.subscriptions, self.AccountID, int(self.DateMonthEndCurrent.timestamp()))
				customers = pool.submit(self.customers, self.AccountID, int(self.DateDayStartCurrent.timestamp()))
				account = pool.submit(self.account, self.AccountID)

				self.set_transactions(transactions.result())
				self.set_subscriptions(subscriptions.result())
				self.set_customers(customers.result())
				self.set_account(account.result())

	def set_locale(self) -> None:
		"""
		Set locale properties
		"""

		locale.setlocale(locale.LC_ALL, '')
		self.DateToday = self.DateToday.astimezone(ZoneInfo(self.TimezonePreference)) if self.TimezonePreference else datetime.datetime.now()
		self.DateDayStartCurrent = self.DateToday.replace(hour=0, minute=0, second=0, microsecond=0)
		self.DateDayEndCurrent = self.DateToday.replace(hour=23, minute=59, second=59, microsecond=999)
		self.DateMonthStartCurrent = self.DateToday.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		self.DateMonthEndCurrent = self.DateToday.replace(day=calendar.monthrange(self.DateToday.year, self.DateToday.month)[1], hour=23, minute=59, second=59, microsecond=999)
		self.DateMonthToDateCurrent = self.DateToday.replace(day=self.DateToday.day, hour=23, minute=59, second=59, microsecond=999)

		self.DateMonthStartPrevious = self.DateMonthStartCurrent + dateutil.relativedelta.relativedelta(months=-1)
		self.DateMonthEndPrevious = self.DateMonthEndCurrent + dateutil.relativedelta.relativedelta(months=-1)
		self.DateMonthToDatePrevious = self.DateDayEndCurrent - dateutil.relativedelta.relativedelta(months=1)

	def set_subscriptions(self, subscriptions: list) -> None:
		"""
		Set properties dependent on retrieving subscriptions data
		"""
		
		self.VolumePending = self.subscriptions_upcoming(subscriptions, self.DateMonthEndCurrent.timestamp())
		self.VolumeTrialing, self.CountTrialingMonthCurrent = self.subscriptions_trialing(subscriptions, epochEnd=int(self.DateMonthEndCurrent.timestamp())).values()
		self.VolumeGrossMonthForecast = self.VolumeGrossMonthCurrent + self.VolumePending + self.VolumeTrialing
		self.VolumeGrossMonthOverMonthPercentChange = self._percentage_diff(self.VolumeGrossMonthPrevious, self.VolumeGrossMonthForecast)
		self.VolumeGrossMonthCurrentPercent = self.VolumeGrossMonthForecast and ((self.VolumeGrossMonthCurrent / self.VolumeGrossMonthForecast) * 100.0) or 0
		self.VolumeTrialingPercent = self.VolumeGrossMonthForecast and ((self.VolumeTrialing / self.VolumeGrossMonthForecast) * 100.0) or 0
		self.VolumePendingPercent = self.VolumeGrossMonthForecast and ((self.VolumePending / self.VolumeGrossMonthForecast) * 100.0) or 0
		self.VolumeGrossMonthToMonthPercentChange = self._percentage_diff(self.VolumeGrossMonthPrevious, self.VolumeGrossMonthForecast)
	
		if self.VolumeGrossMonthToMonthPercentChange > 0:
			self.VolumeGrossMonthOverMonthPercentChangeType = RevenutChangeType.INCREASE
		elif self.VolumeGrossMonthToMonthPercentChange < 0:
			self.VolumeGrossMonthOverMonthPercentChangeType = RevenutChangeType.DECREASE
		else:
			self.VolumeGrossMonthOverMonthPercentChangeType = RevenutChangeType.NOCHANGE

	def set_transactions(self, transactions: list) -> None:
		"""
		Set properties dependent on retrieving charges data
		"""

		self.VolumeGrossToday, self.CountPaymentsToday = self.transactions_date(transactions, self.DateDayStartCurrent.timestamp(), self.DateDayEndCurrent.timestamp()).values()
		self.VolumeGrossMonthCurrent = self.transactions_date(transactions, self.DateMonthStartCurrent.timestamp(), self.DateMonthEndCurrent.timestamp())["amount"]
		self.VolumeGrossMonthPrevious = self.transactions_date(transactions, self.DateMonthStartPrevious.timestamp(), self.DateMonthEndPrevious.timestamp())["amount"]
		self.VolumeGrossMonthToDatePrevious = self.transactions_date(transactions, self.DateMonthStartPrevious.timestamp(), self.DateMonthToDatePrevious.timestamp())["amount"]

	def set_customers(self, customers: list) -> None:
		"""
		Set properties dependent on retrieving customer data
		"""

		self.CountTrialingToday = self.customers_date(customers, int(self.DateDayStartCurrent.timestamp()), int(self.DateDayEndCurrent.timestamp()))

	def set_account(self, account: stripe.Account | stripe.error.StripeError) -> None:
		"""
		Set properties dependent on retrieving acccount data
		"""

		if (type(account) is stripe.Account):
			self.IsAuthorized = True
			self.Status = RevenutAuthorizationType.AUTHORIZED_ID
			self.Code = 200		
			self.AccountName = account.business_profile.name

			accountIconFileLink = self.account_icon(account.stripe_id, account.settings.branding.icon)
			if (accountIconFileLink):
				self.AccountIconURL = accountIconFileLink.url
		elif (isinstance(account, stripe.error.StripeError)):
			self.Status = RevenutAuthorizationType.ERROR
			self.Error = account.user_message
			self.Code = account.http_status

	def account(self, account_id) -> stripe.error.StripeError | stripe.Account:
		account_retrieve = None

		try:
			# https://stripe.com/docs/api/accounts/retrieve
			account_retrieve = stripe.Account.retrieve(account_id)
		except Exception as e:
			logging.error(e)
			return e

		return account_retrieve

	def account_icon(self, account_id: str, fileId: str) -> None | stripe.FileLink:
		accountIconFileLink = None

		try:
			# https://stripe.com/docs/file-upload#download-file-contents
			# https://stripe.com/docs/api/file_links/create
			accountIconFileLink = stripe.FileLink.create(stripe_account=account_id, file=fileId, expires_at=self._icon_expire())
		except Exception as e:
			logging.error(e)

		return accountIconFileLink

	def transactions(self, account_id: str, epochStart: int) -> list:
		"""
		Returns a collection of auto-paginated charges from Stripe

		:param account_id: stripe account identifier
		:param epochStart: request records greater than or equal to Epoch timestamp
		"""
		charges_list = []

		try:
			# https://stripe.com/docs/api/charges/list
			charges = stripe.Charge.list(stripe_account=account_id, limit=100, created={'gte': epochStart})
		except Exception as e:
			logging.error(e)
		else:
			for charge in charges.auto_paging_iter():
				utcToLocaldatetime = time.localtime(charge.created)
				charge.created = time.mktime(utcToLocaldatetime)
				charges_list.append(charge)

		return charges_list

	def transactions_date(self, charges_list: list, epochStart: float, epochEnd: float) -> dict:
		"""
		Returns a collection of successful transactions within a timeframe

		:param charges_list: collection of charges to search on
		:param epochStart: identify records created greater than or equal to Epoch timestamp
		:param epochEnd: identify records created less than or equal to Epoch timestamp
		"""

		transactions_dict = dict(
			amount = 0
			, count = 0
		)
		
		charges_date = list(filter(lambda x: 
									x.created >= epochStart
									and x.created <= epochEnd
									and x.refunded is False 
									and x.status == 'succeeded' 
									and x.disputed is False                                
									, charges_list))
		
		charges_date_amount = sum((charge.amount / 100) for charge in charges_date)
		charges_date_count = len(charges_date)

		transactions_dict['amount'] = charges_date_amount
		transactions_dict['count'] = charges_date_count

		return transactions_dict

	def subscriptions(self, account_id: str, epochEnd: int, status: str | None = None) -> list:
		"""
		Returns a collection of auto-paginated subscriptions from Stripe

		:param account_id: stripe account identifier
		:param epochStart: request records less than or equal to current period end Epoch timestamp
		:param status: status of the subscriptions to retrieve
		"""
		
		subscriptions_list = []
		
		try:
			# https://stripe.com/docs/api/subscriptions/list
			if status:
				subscriptions = stripe.Subscription.list(stripe_account=account_id, limit=100, current_period_end={'lte': epochEnd}, status=status)
			else:
				subscriptions = stripe.Subscription.list(stripe_account=account_id, limit=100, current_period_end={'lte': epochEnd})
		except Exception as e:
			logging.error(e)
		else:
			for s in subscriptions.auto_paging_iter():
				# convert to local timezone
				utcToLocaldatetime1 = time.localtime(s.current_period_end)
				utcToLocaldatetime2 = time.localtime(s.current_period_start)
				s.current_period_end = time.mktime(utcToLocaldatetime1)
				s.current_period_start = time.mktime(utcToLocaldatetime2)
				subscriptions_list.append(s)

		return subscriptions_list

	def subscriptions_trialing(self, subscriptions_list: list, epochEnd: int, epochStart:int | None = None) -> dict:
		"""
		Returns the dollar amount and count of subscriptions that are still in trial phase for current month
		"""

		subscriptions_trialing = []
		subscriptions_dict = dict(
			amount = 0
			, count = 0
		)

		if (epochStart):
			subscriptions_trialing = list(filter(lambda x: (x.status == 'trialing' or x.status == 'canceled') and x.created >= epochStart and x.created <= epochEnd, subscriptions_list))
		else:
			subscriptions_trialing = list(filter(lambda x: x.status == 'trialing' and x.current_period_end <= epochEnd, subscriptions_list))
		
		subscriptions_trialing_amount = sum((subscription.plan.amount / 100) for subscription in subscriptions_trialing)
		subscriptions_trialing_count = len(subscriptions_trialing)

		subscriptions_dict['amount'] = subscriptions_trialing_amount
		subscriptions_dict['count'] = subscriptions_trialing_count

		return subscriptions_dict

	def subscriptions_upcoming(self, subscriptions_list: list, epochEnd: float) -> float:
		"""
		Returns the dollar amount of active subscriptions that haven't been invoiced yet by current month end
		"""

		subscriptions_upcoming = list(filter(lambda x: 
			x.current_period_end <= epochEnd		# subscriptions that will be invoiced before end of month
			and x.status == 'active'				# payment should have been successful before
		, subscriptions_list))

		subscriptions_upcoming_amount = sum((subscription.plan.amount / 100) for subscription in subscriptions_upcoming)
		#subscriptions_upcoming_count = len(subscriptions_upcoming)

		return subscriptions_upcoming_amount

	def customers(self, account_id: str, epochStart: int) -> list:
		"""
		Returns an auto-paginated list of customers from Stripe

		:param account_id: stripe account identifier
		:param epochStart: request records created greater than or equal to Epoch timestamp
		"""
		
		customers_list = []

		try:
			# https://stripe.com/docs/api/customers/list
			customers = stripe.Customer.list(stripe_account=account_id, limit=100, created={'gte': epochStart})
		except Exception as e:
			logging.error(e)
		else:
			for c in customers.auto_paging_iter():
				utcToLocaldatetime = time.localtime(c.created)
				c.created = time.mktime(utcToLocaldatetime)
				customers_list.append(c)

		return customers_list
	
	def customers_date(self, customers_list: list, epochStart: float, epochEnd: float) -> int:
		"""
		Returns the number of customers created in the requested timespan
		:param epochStart: records created greater than or equal to timestamp
		:param epochEnd: records created less than or equal to timestamp
		"""
		
		customers_count = 0

		customers_date = list(filter(lambda x:
			x.created >= epochStart
			and x.created <= epochEnd
		, customers_list))

		customers_count = len(customers_date)

		return customers_count

	def token(self, auth_code: str) -> stripe.error.StripeError | dict:
		"""
		Used both for turning an authorization_code into an account connection, and for getting a new access token using a refresh_token
		https://stripe.com/docs/connect/oauth-reference#post-token

		:param auth_code: authorization code returned from Stripe Connect
		"""

		response = None

		try:
			response = stripe.OAuth.token(grant_type='authorization_code', code=auth_code)
		except Exception as e:
			logging.error(e)
			return e

		return response

	def user_id(self, token: dict) -> str:
		"""
		Returns the `stripe_user_id` from a Stripe token
		"""
		account_id = None
		
		if (token.__contains__('stripe_user_id')):
			account_id = token['stripe_user_id']

		return account_id

	def revoke(self, account_id: str) -> str | None:
		"""
		Used for revoking access to an account
		"""

		response = None
		client_id = os.getenv('STRIPE_CLIENT_ID')

		try:
			# https://stripe.com/docs/connect/oauth-reference#post-deauthorize
			response = stripe.OAuth.deauthorize(client_id=client_id, stripe_user_id=account_id)
		except Exception as e:
			response = e.code
		
		return response

	def _icon_expire(self, timeDeltaMinutes: int = 5):
		"""
		Returns an expiration date
		"""
		return int((datetime.datetime.now() + datetime.timedelta(minutes=timeDeltaMinutes)).timestamp())

	def _percentage_diff(self, previous: float, current:float) -> float:
		"""
		Returns the percent change between previous and current period numbers
		"""
		if current == previous:
			return 0
		try:
			return ((current - previous) / previous) * 100.0
		except ZeroDivisionError:
			return float('inf')

def main() -> None:
	"""
	Run RevenutStripe independent of API
	"""
	
	#mystripe = RevenutStripe(AuthorizationCode="123")
	mystripe = RevenutStripe(AccountID=os.getenv('STRIPE_ACCOUNT_ID'), TimezonePreference="America/Los_Angeles")

	print(f"""
		Status: {mystripe.Status}
		Code: {mystripe.Code}
		IsAuthorized: {mystripe.IsAuthorized}
		Error: {mystripe.Error}
		VolumeGrossToday: {mystripe.VolumeGrossToday}
		VolumeGrossMonthCurrent: {mystripe.VolumeGrossMonthCurrent}
		VolumePending: {mystripe.VolumePending}
		VolumeGrossMonthTrialing: {mystripe.VolumeTrialing}
		VolumeGrossMonthForecast: {mystripe.VolumeGrossMonthForecast}
		VolumeGrossMonthPrevious: {mystripe.VolumeGrossMonthPrevious}
		VolumeGrossMonthOverMonthPercentChangeType: {mystripe.VolumeGrossMonthOverMonthPercentChangeType}
	""")

if __name__ == '__main__':
	main()