select dodsvaluation.dbo.RecluseValuationReport.IDSBL,
--[DODS].[dbo].[IROptionsLegsSummary].PayDate,
--[DODS].[dbo].[IROptionsLegsSummary].ResetDate,
[DODS].[dbo].[TradeInfoIROptions].EffectiveDate,
dodsvaluation.dbo.RecluseValuationReport.OptionTypeDesc,
dodsvaluation.dbo.RecluseValuationReport.TradeDate,
dodsvaluation.dbo.RecluseValuationReport.ExpirationDate,
dodsvaluation.dbo.RecluseValuationReport.SBL,
dodsvaluation.dbo.RecluseValuationReport.Delta,
dodsvaluation.dbo.RecluseValuationReport.Underlying,
dodsvaluation.dbo.RecluseValuationReport.StrikeCap

into #temp

--from [DODS].[dbo].[IROptionsLegsSummary]
--join dodsvaluation.dbo.RecluseValuationReport on dodsvaluation.dbo.RecluseValuationReport.IDSBL=[DODS].[dbo].[IROptionsLegsSummary].BBGId and ObservationDate ='2024-06-24' --and OptionTypeDesc = 'Interest Rate Cap' 

from [DODS].[dbo].[TradeInfoIROptions]
join dodsvaluation.dbo.RecluseValuationReport on dodsvaluation.dbo.RecluseValuationReport.IDSBL=[DODS].[dbo].[TradeInfoIROptions].BBGId and ObservationDate ='2024-06-24' --and OptionTypeDesc = 'Interest Rate Cap' 

select * from #temp

drop table #temp


--#Seperate Query#--
select InternalPortfolio,TradeType,AL,sum(Notional) as Notional,
sum(SBL) as Valuation, sum(Delta) as Delta, sum(Rho) as Rho,
sum(Gamma) as Gamma, sum(Vega) as Vega, sum(Theta) as Theta
from dodsvaluation.dbo.RecluseValuationReport where ObservationDate ='2024-06-24'
Group by InternalPortfolio,TradeType,AL
Order by InternalPortfolio,TradeType,AL