from pydantic import BaseModel

import datetime

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