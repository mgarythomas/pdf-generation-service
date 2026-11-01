# Research: AWS Lambda Form Factors & Invocation Patterns

**Document Status:** Research Summary
**Audience:** Digital Platform Engineering Team
**Purpose:** Reference document clarifying the different AWS Lambda options now available, including the new HTTP-native form factors that enable running web frameworks (e.g. Next.js) on Lambda.
**Last Reviewed:** 2026-10-25

---

## 1. Executive Summary

AWS Lambda is no longer a single, monolithic compute model. It now spans **three distinct form factors** (built on the same Firecracker isolation technology), each designed for a different programming model, plus several **invocation methods**, **edge/streaming variants**, and **concurrency controls** that layer on top. This document captures the current landscape so the team can reason about which Lambda option fits a given workload — and crucially, how the newest **Lambda Web Functions** form factor changes the equation for running HTTP web apps like Next.js on Lambda.

> The most common source of confusion is treating "Lambda" as one thing. It is now a family of related but distinct compute form factors. Pick the **form factor** based on the programming model (event-driven vs HTTP-native vs stateful sandbox), then pick the **invocation method** and **concurrency settings** based on how the function is triggered and what latency profile it needs.

---

## 2. Lambda Form Factors (what you deploy)

All three form factors share the same underlying Firecracker microVM isolation but differ in programming model, concurrency behaviour, and billing.

| Form Factor | Programming Model | Concurrency | Billing | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Event Function** | Event-driven, single handler per invocation | 1 request per execution env | Wall-clock time | Event processing, queue consumers, service-triggered workloads |
| **Web Function** *(new)* | HTTP-native — code listens on a port | Up to **128 concurrent requests** per execution env | Active CPU time + memory | Web applications, API backends, SSR, AI inference streaming |
| **MicroVM** | Stateful sandbox, customer-managed lifecycle | Customer-managed | — | Running untrusted / user-generated code in isolation |

### 2.1 Event Functions (the classic Lambda)

- Stateless: each invocation is independent.
- The function receives an event, processes it, returns a response.
- Max wall-clock duration: **15 minutes**.
- Ideal for event processing, queue consumers, and invocations triggered by other AWS services.

### 2.2 Web Functions (new HTTP-native form factor)

- Run a standard **port-listening HTTP server** (Express, Hono, Fastify, **Next.js**, Flask, Spring Boot, etc.) with **no code rewrite and no adapter**.
- The only convention is reading the `AWS_LAMBDA_HTTP_ENDPOINT` environment variable to learn which host/port the server must listen on.
- Each execution environment handles up to **128 concurrent requests**, so traffic bursts share warm environments instead of cold-starting one env per request.
- **Active CPU billing**: you are billed for CPU time actually used, not time spent waiting on a DB query or downstream API call. Memory is metered for as long as the execution environment exists. This is a meaningful cost benefit for I/O-heavy SSR and API workloads.
- Built-in HTTPS endpoint, multi-region latency-based routing via one global URL, canary/weighted rollouts between revisions, and works behind CloudFront with origin access control (OAC) for a private-origin pattern.
- Single-command deploy: `aws lambda-web deploy --name my-web-app --code ./my-app`.
- GA regions at launch: `us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`, `eu-west-1`.
- Runtime at launch: Node.js 24 (`nodejs24.x`) on Arm64. VPC connectivity is supported.

A minimal Express example, showing how close to "run it locally" the programming model is:

```js
import express from 'express';

const app = express();
const [host, port] = process.env.AWS_LAMBDA_HTTP_ENDPOINT.split(':');

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Lambda Web Functions!' });
});

app.listen(port, host, () => {
  console.log(`Server running on port ${port}`);
});
```

### 2.3 MicroVMs

- Isolated, stateful sandbox environments with customer-managed lifecycles.
- Intended for running untrusted or user-generated code.
- Not covered in depth here; mentioned for completeness so the team can distinguish it from the other two Lambda form factors.

---

## 3. Invocation Methods (how a function is run)

These invocation methods apply to both Event Functions and Durable Functions:

- **Synchronous (`RequestResponse`)** — caller blocks until Lambda returns the response. Capped at 15 minutes. The caller is responsible for retries on error. Common for web APIs and interactive workloads.
- **Asynchronous (`Event`)** — Lambda queues the event and returns immediately. Lambda handles retries automatically and can route success/failure outcomes to a destination. Ideal for fire-and-forget and background processing.
- **Event source mapping (poll-based)** — Lambda itself polls a stream/queue source (SQS, Kinesis, DynamoDB Streams, MSK, self-managed Kafka) and invokes the function with **batches of records**. Distinct from a service *pushing* to Lambda synchronously.
- **Response streaming (`InvokeWithResponseStream`)** — the function streams the payload back incrementally rather than buffering the whole response. Improves time-to-first-byte for LLM/chat and large payloads; works through API Gateway proxy integration and Function URLs. Bypasses the 6 MB synchronous-payload cap; soft limit of ~20 MB with bandwidth throttling on overflow.
- **Function URLs** — a dedicated HTTPS endpoint Lambda provisions for a function; supports both buffered and streaming responses, and IAM or unauthenticated access.

---

## 4. Durable Functions (long-running, stateful)

A distinct **function type** (in addition to Event Functions) for long-running, stateful workflows using checkpointing. An execution can pause (e.g. on a `wait`) and resume hours or days later without incurring compute charges while paused.

- **Max duration**: up to **1 year** (asynchronous invocation). Synchronous still capped at 15 minutes.
- **Stateful**: checkpoint log is replayed on resume so the function continues from where it paused.
- **Qualified ARN required**: must invoke with a version, alias, or `$LATEST`. An in-flight execution is pinned to the code version that started it, so publishing a new version affects only new executions.
- **Error handling**: supports dead-letter queues (DLQs) but **does not** support Lambda destinations.
- **Best practice**: use numbered versions or aliases in production rather than `$LATEST`, because `$LATEST` executions can resume on updated code and produce non-determinism errors.

---

## 5. HTTP / Web Framework Support (focus area)

This is the section most relevant to the team's current interest in running Next.js-style HTTP workloads on Lambda. There are **three distinct approaches**, and they are often conflated. Be explicit about which one is meant.

### 5.1 AWS Lambda Web Functions (newest — native HTTP form factor)

See §2.2. This is a **new form factor**, not a wrapper. The HTTP server runs natively on Lambda with multi-concurrency and active CPU billing. This is the option that most directly answers "Lambda that can now be used for HTTP requests to handle things like Next.js" without any adapter or code rewrite.

### 5.2 AWS Lambda Web Adapter (LWA) — the adapter approach

A Rust-based Lambda extension that translates Lambda's event payload into a normal HTTP request and forwards it to a web server running in the same execution environment.

- Your framework still runs as a normal HTTP server; the adapter bridges the Lambda event model to HTTP.
- Supports **response streaming** via Function URLs or `InvokeWithResponseStream` — important for Next.js streaming SSR, where the first byte can be flushed before the full response is ready.
- Framework-agnostic: Express, Next.js, Flask, Spring Boot, ASP.NET, Laravel — "anything that speaks HTTP 1.1/1.0".
- Differs from Web Functions in that it still uses the **single-invocation-per-event model** with wall-clock billing. It is a compatibility shim, not a new programming model.

### 5.3 OpenNext / SST (community path)

A third option the team may encounter: **OpenNext** (often used via the SST framework) compiles a Next.js app into Lambda Event Functions plus S3/CloudFront, mimicking Vercel's deployment model. It uses the **event-driven model**, not Web Functions. It is a community project, not an AWS product, but has been the most common way teams have run full Next.js on AWS to date. Do not conflate it with the official AWS form factors.

### 5.4 Comparison: Web Functions vs Web Adapter vs OpenNext

| | Web Functions (new) | Web Adapter (LWA) | OpenNext / SST |
| :--- | :--- | :--- | :--- |
| Code changes needed | None (read one env var) | None | Build-time compile step |
| Programming model | Native HTTP server | Event handler bridged to HTTP | Event-driven (Vercel-style) |
| Concurrency per env | Up to 128 concurrent requests | 1 per invocation | 1 per invocation |
| Billing | Active CPU + memory | Wall-clock time | Wall-clock time |
| Response streaming | Native | Supported (Function URL / `InvokeWithResponseStream`) | Supported |
| Multi-region routing | Built-in (latency-based) | Manual (CloudFront / Route 53) | Manual (CloudFront / Route 53) |
| Regions | 5 at launch | All commercial regions | All commercial regions |
| Status | New form factor, GA in limited regions | Mature, broadly available | Community project |
| Maintainer | AWS | AWS Labs | Community |

---

## 6. Edge & Related Variants (commonly confused)

- **Lambda@Edge** — runs Lambda functions in CloudFront edge locations (closer to users) to inspect/transform requests and responses. It is a deployment target, not a new invocation protocol.
- **CloudFront Functions** — a *separate* (not Lambda) lightweight JS runtime for CDN-edge transformations. Smaller scale, lower latency, much more restrictive than Lambda@Edge. Worth distinguishing because teams often say "Lambda at the edge" when they mean CloudFront Functions.

---

## 7. Concurrency Controls (orthogonal to invocation)

- **Reserved concurrency** — guarantees a minimum number of concurrent executions for a function.
- **Provisioned concurrency** — pre-initialises execution environments to eliminate cold starts; targets double-digit-millisecond latency for interactive APIs.
- **Account concurrency limit** — default 1,000 concurrent executions per region across all Event Functions.

---

## 8. Context: Relevance to Our DMZ Architecture

Our `dmz_api_deployment_patterns_confluence.md` puts the **Next.js BFF in Pattern 1** on **DMZ EKS pods**. If the team is now considering Lambda for that role, the relevant candidate is **Lambda Web Functions**, because:

- It satisfies the "single DMZ compute footprint" advantage called out in §3.2 of the DMZ doc.
- Multi-concurrency + provisioned concurrency address cold-start concerns for interactive web traffic.
- The HTTP-native model matches the existing Next.js API Route programming model in Pattern 1.
- The CloudFront OAC private-origin pattern aligns with the Imperva/F5 ingress controls in §2.

**Caveats / open questions to verify before committing**:

- **Regional availability**: Web Functions launched in only 5 regions. Our DMZ doc references Aurora in `ap-southeast-2` (see §5.1 of `dmz_api_deployment_patterns_confluence.md`). `ap-southeast-2` is **not** in the Web Functions launch region list, so Web Functions availability in our primary region must be confirmed before relying on it for the BFF tier.
- **Maturity**: Web Functions is a brand-new form factor. The team should weigh operational simplicity against maturity.
- **VPC connectivity**: Web Functions supports VPC connectivity at launch, which is required to reach the cross-VPC `execute-api` VPC Endpoint in our Pattern 1 design.

---

## 9. Quick Mental Model

> Pick a **form factor** (Event vs Web vs MicroVM) based on the programming model and concurrency profile. Pick a **function type** (Event vs Durable) based on how long the work runs and whether it needs to pause/resume. Then pick an **invocation method** based on who triggers it and whether the caller needs the result now (sync), later (async), in batches (event source mapping), or streamed back (response streaming). Concurrency settings and Lambda@Edge are independent configuration levers on top of that.

---

## 10. Sources

- [Announcing AWS Lambda Web Functions](https://aws.amazon.com/blogs/aws/announcing-aws-lambda-web-functions-for-fast-consistent-web-app-performance-anywhere/) — AWS News Blog
- [Understanding Lambda Event Function invocation methods](https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html) — AWS Lambda Developer Guide
- [Invoking Lambda durable functions](https://docs.aws.amazon.com/lambda/latest/dg/durable-invoking.html) — AWS Lambda Developer Guide
- [Response streaming for Lambda Event Functions](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html) — AWS Lambda Developer Guide
- [Configuring provisioned concurrency for a function](https://docs.aws.amazon.com/lambda/latest/operatorguide/initialization-pc.html) — AWS Lambda Operator Guide
- [Understanding Lambda Event Function scaling](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html) — AWS Lambda Developer Guide
- [AWS Lambda@Edge](https://aws.amazon.com/lambda/edge/) — AWS product page
- [aws-lambda-web-adapter](https://github.com/awslabs/aws-lambda-web-adapter) — AWS Labs GitHub
- [lwa-nextjs-response-streaming-example](https://github.com/aws-samples/lwa-nextjs-response-streaming-example) — AWS Samples GitHub
- [Using response streaming with AWS Lambda Web Adapter](https://aws.amazon.com/blogs/compute/using-response-streaming-with-aws-lambda-web-adapter-to-optimize-performance/) — AWS Compute Blog

> Content from the above sources was paraphrased and rephrased for compliance with licensing restrictions. Verify current feature availability and region support against the official AWS documentation before architecting production workloads.
