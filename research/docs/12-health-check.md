# Health Check — `GET /v1/responses/health`

> Source: https://docs.concentrate.ai/api-reference/endpoint/health
> Captured: 2026-02-16

## Overview

Simple endpoint to verify the Concentrate AI API is operational. **No authentication required.**

## Request

```
GET https://api.concentrate.ai/v1/responses/health
```

No headers or body required.

## Response

### Success (200 OK)
Empty response body with 200 status code. Our empirical test returns `{"status":"healthy"}`.

### Failure (5xx)
If the API is experiencing issues, you may receive a 5xx status code or no response.

## Use Cases

1. **Uptime Monitoring** — Poll every 60 seconds
2. **Pre-Flight Checks** — Verify API before critical requests (we added this as smoke_test.py Check 0)
3. **Load Balancer Health Checks** — AWS ALB, Nginx upstream
4. **Circuit Breaker Integration** — Open circuit after 3 consecutive failures

## Health Check Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| **Availability** | % of successful health checks | < 99.9% |
| **Response Time** | Average latency | > 1000ms |
| **Error Rate** | % of failed checks | > 1% |
| **Consecutive Failures** | Failures in a row | >= 3 |

## Status Page

Real-time API status: [status.concentrate.ai](https://status.concentrate.ai)

## Related Documentation

- [Error Handling](/api-reference/endpoint/errors)
- [Create Response](/api-reference/endpoint/create-response)
