# Experience Analytics
Roblox's experience analytics API allows developers to query a plethora of analytic metrics. These metric include daily active users, retention, monetization, acquisition and performance metrics. The analytics API is a broad subject with numerous essential concepts. These concepts include, metrics, dimensions, and breakdowns.

### Metrics, dimensions, and breakdowns
**Metrics** are each different analytic. These include daily active users, day 1 retenion rate, funnel steps, paying users conversion rate, among many others.

**Dimensions** are how the values may be *drilled down* by. For instance, daily active users includes two dimensions among others. They include gender and platform. You could filter by platform to only include phones and you may breakdown by gender to determine the gender of daily active phone users. Dimensions are how a metric can be filtered and broken down.

Roblox maintains a list of the supported metrics and dimensions on the [Creator Hub](https://create.roblox.com/docs/cloud/guides/analytics/metrics#funnels).

### Basic usage - daily active users by platform
The following example applies the basic concepts discussed above. The example queries the `DailyActiveUsers` metric and breaks the data down by `Platform`. This means the result will return data points for daily active users for each platform.

```py
operation = experience.query_analytic_metric(
    "DailyActiveUsers",
    start_time=datetime.datetime(2025, 7, 1),
    end_time=datetime.datetime(2026, 7, 1),
    breakdown=["Platform"]
)

result = operation.wait()
```

Often the result will be available instantly. In those circumstances, `Operation.wait` is non-blocking. However, sometimes Roblox needs to process data and it may take a few seconds longer. `wait` will automatically await the query's completion.

In this circumstance, we have broken the data down the platform. We can iterate through a dictionary of breakdown-data points pairs in the following manner:

```py
for breakdown, datapoints in result.data_points.items():
    print(list(breakdown)[0], datapoints)
>>> <rblxopencloud.ExperienceAnalyticsBreakdown dimension='Platform' value='Phone'> [<rblxopencloud.ExperienceAnalyticsDatapoint time=datetime.datetime() value=67>, ...]
    ...
```
Naturally, this list is going to be extremely large. This is because there will be a value for each platform, each day of the year.

### How breakdowns are handled
Breakdowns can vary in complexity. Sometimes there will be no breakdown and in other occasions you may query a metric to be broken down by two or more breakdowns. This makes them complex to handle consistently in the library.

The library stores breakdowns as [`frozenset`][frozenset] objects within [`ExperienceAnalyticsResult.data_points][rblxopencloud.ExperienceAnalyticsResult.data_points]. Sets do not consider order, meaning that they do not create issues when breaking down by multiple dimensions. The set must be frozen to be used as a key.

Some tips for working with breakdown sets:
- If you are not breaking down by any dimension, the data points are stored at `data_points[frozenset()]`. That is, an empty frozen set represents no break down.
- If you want to get a break down value from a frozenset, you must convert it into a list or iterable. These are two methods:
    - `list(breakdown)[0].value` works for a single breakdown dimension being used.
    - `next(iter(breakdown)).value` is another solution for a single breakdown dimension.
    - If you are dealing with numerous breakdowns, an example of converting it to a list is `", ".join(breakdown)`
- To create a breakdown key, you can create a breakdown object and convert it to a frozen set. An example is shown below.

```py
breakdown = rblxopencloud.ExperienceAnalyticsBreakdown("Platform", "Computer")
breakdown_key = frozenset({breakdown})

result.datapoints[breakdown_key]
>>> [<rblxopencloud.ExperienceAnalyticsDatapoint time=datetime.datetime() value=100>, ...]
```