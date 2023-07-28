from pydantic import BaseModel
from zoneinfo import ZoneInfo

import os
import calendar
import datetime
import dateutil.relativedelta
import locale
import logging

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

	def init_locale(self) -> None:
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

	def init_account(self, account: stripe.Account | None) ->None:
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