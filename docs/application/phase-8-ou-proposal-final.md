# Reliability Automation and Software Engineering Practice in Continuous Delivery Environments

## Background

Continuous delivery increasingly relies on automation for deployment, monitoring and recovery, yet operational reliability remains a socio-technical problem: automation changes both system behaviour and the decisions engineers make when failures occur. Empirical studies of continuous delivery show that deployment practice is shaped by automation, architecture, organisational constraints and operations concerns [1,2]. Large-scale incident studies also show that online-service failures require prioritisation and diagnosis rather than purely mechanical response [3], while service-level fault-injection research demonstrates that controlled failures can expose resilience weaknesses in microservice systems [4].

Preliminary mapping for this project suggests that these strands are often studied separately. Technical studies commonly evaluate systems, faults or incident data, whereas direct evidence about engineers' diagnosis, recovery and escalation decisions is less consistently coupled to matched technical conditions. The full scoping review remains to be completed, so this is a research motivation rather than a claim that the literature gap has already been exhaustively established.

## Aim and Method

The aim is to investigate reliability automation as a socio-technical intervention by combining reproducible technical experiments with a separately ethics-reviewed study of software-engineering decisions.

**RQ1:** Under controlled fault scenarios in a reproducible transactional service system, how do different recovery-automation strategies affect recovery time, failure impact and required intervention?

**RQ2:** How does automation-assisted incident response influence software engineers' diagnosis, recovery and escalation decisions during structured continuous-delivery tasks?

The empirical object will be **OrderFlow**, a purpose-built cloud-native transactional benchmark. Its initial bounded slice contains an `order-api` service and an `inventory` dependency deployed on Kubernetes with synthetic order traffic. OrderFlow was selected because it provides independently deployable services, observable dependency failures, deterministic workload and reset boundaries, and enough interaction to study recovery while remaining small enough for repeated controlled experiments. This directly fixes the software under study rather than treating ?microservices? as an unspecified domain. The benchmark's simplicity is also an external-validity limitation that will be reported rather than hidden.

For RQ1, trials use versioned workloads, controlled service-termination and dependency-latency faults, a shared detector and matched recovery conditions. The technical evidence stream records structured controller and workload events, recovery actions, environment/version provenance and validity decisions; OpenTelemetry traces provide corroborating observability rather than replacing the primary event record. Outcomes include recovery time, failure impact and intervention counts. Detection latency is retained as a detector-fidelity and condition-balance measure because the detector is shared rather than treated as an automation effect.

A pre-application pilot has already established methodological feasibility: all 50 planned technical slots were resolved from 53 preserved attempts, yielding 50 valid observations while retaining three invalid attempts without imputation. The results are descriptive pilot evidence only. They do not establish statistical significance, production readiness or universal superiority of automated recovery. The doctoral study will use the pilot to refine scenarios and justify any later inferential design rather than retrospectively converting the pilot into confirmatory evidence.

RQ2 requires a separate participant evidence stream. The protocol uses matched OrderFlow incident tasks in a within-participant, counterbalanced design. In the manual-decision condition, participants diagnose an incident and choose recovery or escalation from a bounded interface. In the automation-assisted condition the same form of evidence is accompanied by a transparent recommendation that may be correct or incorrect; participants may accept, override or escalate. Primary measures are diagnosis accuracy, recovery-decision appropriateness and escalation appropriateness. Decision time, workload and behavioural reliance calibration are secondary measures. An initial 8?12-participant feasibility study will test task operation and measurement burden descriptively; a later main study would require an ethics-approved protocol and a justified sample-size and analysis plan. Participant recruitment and data collection will not begin before the required institutional approvals.

The two streams will be analysed separately and integrated at the level of research interpretation, not by pooling technical recovery times with human decision measures. Threats to validity include the purpose-built benchmark, limited fault families, learning effects in participant tasks, professional recruitment constraints and the difference between controlled incidents and production work.

## Relevance

The project contributes a reproducible way to examine reliability automation without treating system telemetry as a proxy for human reasoning. For software-engineering research, it links controlled technical evidence with direct evidence of diagnosis and recovery decisions while preserving clear validity boundaries. For practice, it may identify situations in which automation changes recovery performance, intervention requirements or reliance decisions, helping teams reason about when automated recovery should act autonomously and when human judgement or escalation remains important.

The work aligns with the Open University's Software Engineering and Design emphasis on automated software engineering, adaptive systems, empirical studies of software development and software engineering in human context.

## Your suitability

I hold a First-Class BSc and a Distinction MSc in Computer Science and have professional software-engineering and release-management experience involving Java, web development, CI/CD, Jenkins/GitHub Actions, Docker and Kubernetes. Before application I have also built the bounded OrderFlow research environment, validated reproducible Kubernetes execution, completed the technical pilot and prepared the human-participant protocol and data-management boundary. This preparation demonstrates that the proposed work is technically feasible while also showing where doctoral research is still required: a completed literature synthesis, broader experimental validation, ethics-approved participant work and integrated analysis.

## References

[1] Shahin, M., Babar, M. A., Zahedi, M. and Zhu, L. (2017). Beyond Continuous Delivery: An Empirical Investigation of Continuous Deployment Challenges. ESEM. DOI: 10.1109/ESEM.2017.18.

[2] Shahin, M., Zahedi, M., Babar, M. A. and Zhu, L. (2019). An Empirical Study of Architecting for Continuous Delivery and Deployment. Empirical Software Engineering, 24, 1061?1108. DOI: 10.1007/s10664-018-9651-4.

[3] Chen, J. et al. (2020). How Incidental are the Incidents? Characterizing and Prioritizing Incidents for Large-Scale Online Service Systems. ASE.

[4] Meiklejohn, C. et al. (2021). Service-Level Fault Injection Testing. SoCC.
