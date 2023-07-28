from pydantic import BaseModel
from zoneinfo import ZoneInfo

import os
import calendar
import datetime
import dateutil.relativedelta
import locale
import logging
import time

import stripe

class RevenutStripe(BaseModel):
	#region Properties
	IsAuthorized: bool = False
	Status:str | None = None
	AccountID: str | None = None
	AccountName: str | None = None
	AccountIconURL: str | None = None
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

		stripe.api_key = os.getenv('API_KEY_STRIPE')
		stripe.log = 'info'

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
		self.DateMonthToDatePrevious = self.DateMonthStartPrevious.replace(day=self.DateToday.day, hour=23, minute=59, second=59, microsecond=999)

	def set_transactions(self, transactions: list) -> None:
		"""
		Set transaction properties
		"""

		self.VolumeGrossToday, self.CountPaymentsToday = self.transactions_date(transactions, self.DateDayStartCurrent.timestamp(), self.DateDayEndCurrent.timestamp()).values()
		self.VolumeGrossMonthCurrent = self.transactions_date(transactions, self.DateMonthStartCurrent.timestamp(), self.DateMonthEndCurrent.timestamp())["amount"]
		self.VolumeGrossMonthPrevious = self.transactions_date(transactions, self.DateMonthStartPrevious.timestamp(), self.DateMonthEndPrevious.timestamp())["amount"]
		self.VolumeGrossMonthToDatePrevious = self.transactions_date(transactions, self.DateMonthStartPrevious.timestamp(), self.DateMonthToDatePrevious.timestamp())["amount"]
		self.VolumeGrossMonthToMonthPercentChange = self._percentage_diff(self.VolumeGrossMonthToDatePrevious, self.VolumeGrossMonthCurrent)

	def set_account(self, account: stripe.Account | None) ->None:
		"""
		Set account properties
		"""

		if (account):
			self.AccountName = account.business_profile.name
			accountIconFileLink = self.account_icon(account.stripe_id, account.settings.branding.icon)
			if (accountIconFileLink):
				self.AccountIconURL = accountIconFileLink.url

	def account(self, account_id) -> None | stripe.Account:
		account_retrieve = None

		try:
			# https://stripe.com/docs/api/accounts/retrieve
			account_retrieve = stripe.Account.retrieve(account_id)
		except Exception as e:
			logging.error(e)

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

	def transactions(self, account_id:str, epochStart: int) -> list:
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

def main():
	print("Calling Stripe API...")
	mystripe = RevenutStripe()

	print(f"""
		Status: {mystripe.Status}
		VolumeGrossToday: {locale.currency(mystripe.VolumeGrossToday)}
		VolumeGrossMonthCurrent: {locale.currency(mystripe.VolumeGrossMonthCurrent)}
		VolumePending: {locale.currency(mystripe.VolumePending)}
		VolumeGrossMonthTrialing: {locale.currency(mystripe.VolumeTrialing)}
		VolumeGrossMonthForecast: {locale.currency(mystripe.VolumeGrossMonthForecast)}
	""")

if __name__ == '__main__':
	main()