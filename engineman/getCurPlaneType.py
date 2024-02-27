from utilref import *

result = None
try:
    result = (
        Port8111.get(Port8111.QueryType.indicator)
        .expectValid()
        .expectToBe(Port8111.BeanIndicatorBase.IndicatorType.air)
        .type
    )
except Port8111.FetchFailure:
    ...
print(result)
