import html
import os

def escape(s):
    return html.escape(s, quote=True)

class DrawIOBuilder:
    def __init__(self, page_width=3200, page_height=3850):
        self.cells = []
        self.cell_id = 2
        self.page_width = page_width
        self.page_height = page_height

    def new_id(self):
        cid = f"cell_{self.cell_id}"
        self.cell_id += 1
        return cid

    def add_box(self, label, x, y, w, h, style, parent="1", id=None):
        if id is None:
            id = self.new_id()
        cell = f'<mxCell id="{id}" value="{escape(label)}" style="{style}" vertex="1" parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'
        self.cells.append(cell)
        return id

    def add_aws_card(self, title, lines, x, y, w, h, res_icon, icon_color, card_style, parent="1"):
        box_id = self.new_id()
        line_breaks = "<br>".join([f"• {line}" if not line.startswith("•") and not line.startswith("<b>") else line for line in lines])
        label = f"<b>{title}</b><br>{line_breaks}" if lines else f"<b>{title}</b>"
        
        # Add card container
        self.add_box(label, x, y, w, h, card_style, parent=parent, id=box_id)
        
        # Add AWS4 official icon on the top-left
        icon_style = (f"sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;"
                      f"fillColor={icon_color};strokeColor=none;dashed=0;"
                      f"verticalLabelPosition=bottom;verticalAlign=top;align=center;"
                      f"html=1;fontSize=10;fontStyle=0;aspect=fixed;pointerEvents=1;"
                      f"shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{res_icon};")
        self.add_box("", x + 8, y + 8, 42, 42, icon_style, parent=parent)
        return box_id

    def add_edge(self, source, target, label="", style="", id=None):
        if id is None:
            id = self.new_id()
        default_style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;fontSize=10;fontStyle=1;strokeWidth=2;"
        full_style = default_style + style
        cell = f'<mxCell id="{id}" value="{escape(label)}" style="{full_style}" edge="1" source="{source}" target="{target}" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>'
        self.cells.append(cell)
        return id

    def to_xml(self):
        content = "\n".join(self.cells)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-09-28T15:15:00.000Z" agent="Antigravity AWS Architecture Generator" version="24.0.0" type="device">
  <diagram id="aws_deployment_architecture" name="AWS Enterprise Architecture (Official AWS Icons)">
    <mxGraphModel dx="{self.page_width}" dy="{self.page_height}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.page_width}" pageHeight="{self.page_height}" background="#F8FAFC" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
{content}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""

def build_diagram():
    b = DrawIOBuilder(3200, 3850)

    # Base Container Styles
    title_style = "shape=rectangle;whiteSpace=wrap;html=1;fillColor=#0F172A;strokeColor=#1E293B;fontColor=#FFFFFF;fontStyle=1;fontSize=16;rounded=1;shadow=1;align=left;spacingLeft=25;"
    legend_style = "shape=rectangle;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;fontColor=#1E293B;fontSize=10;rounded=1;shadow=0;align=left;spacingLeft=15;"
    
    # Official AWS Group Styles
    acc_network_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#F0F9FF;strokeColor=#0284C7;strokeWidth=2;dashed=0;fontColor=#0369A1;fontStyle=1;fontSize=13;startSize=32;rounded=1;arcSize=4;"
    acc_dmz_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#4F46E5;strokeWidth=2;dashed=0;fontColor=#3730A3;fontStyle=1;fontSize=13;startSize=32;rounded=1;arcSize=4;"
    acc_internal_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#059669;strokeWidth=2;dashed=0;fontColor=#065F46;fontStyle=1;fontSize=13;startSize=32;rounded=1;arcSize=4;"
    acc_kafka_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#FFF7ED;strokeColor=#EA580C;strokeWidth=2.5;dashed=0;fontColor=#9A3412;fontStyle=1;fontSize=13;startSize=32;rounded=1;arcSize=4;shadow=1;"
    acc_onprem_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#1E3A8A;strokeWidth=2.5;dashed=0;fontColor=#1E3A8A;fontStyle=1;fontSize=13;startSize=32;rounded=1;arcSize=4;shadow=1;"
    acc_saas_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#FAF5FF;strokeColor=#7E22CE;strokeWidth=2.5;dashed=0;fontColor=#581C87;fontStyle=1;fontSize=13;startSize=32;rounded=1;arcSize=4;shadow=1;"

    vpc_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#64748B;strokeWidth=1.5;dashed=1;fontColor=#334155;fontStyle=1;fontSize=11;startSize=26;rounded=1;arcSize=3;"
    cluster_style = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#94A3B8;strokeWidth=1.5;dashed=0;fontColor=#0F172A;fontStyle=1;fontSize=11;startSize=26;rounded=1;arcSize=4;"
    account_services_band = "shape=swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#94A3B8;strokeWidth=1;dashed=1;fontColor=#475569;fontStyle=2;fontSize=11;startSize=24;rounded=1;"

    # Card Styles with spacingLeft=56 for the AWS icon
    card_base = "shape=rectangle;whiteSpace=wrap;html=1;rounded=1;arcSize=6;shadow=1;align=left;verticalAlign=middle;spacingLeft=56;spacingRight=10;fontSize=10;"
    
    card_compute = card_base + "fillColor=#FFF7ED;strokeColor=#EA580C;fontColor=#7C2D12;" # Orange
    card_network = card_base + "fillColor=#FAF5FF;strokeColor=#8C4FFF;fontColor=#581C87;" # Purple
    card_storage = card_base + "fillColor=#F0FDF4;strokeColor=#7AA116;fontColor=#14532D;" # Green
    card_security = card_base + "fillColor=#FFF1F2;strokeColor=#CC2264;fontColor=#881337;" # Pink/Crimson
    card_database = card_base + "fillColor=#EFF6FF;strokeColor=#2E27AD;fontColor=#1E3A8A;" # Blue
    card_integration = card_base + "fillColor=#FDF2F8;strokeColor=#E7157B;fontColor=#831843;" # Magenta
    
    # Custom Highlighted Integration Cards
    card_ncore = card_base + "fillColor=#EFF6FF;strokeColor=#1E3A8A;strokeWidth=2;fontColor=#172554;"
    card_map = card_base + "fillColor=#FFFBEB;strokeColor=#B45309;strokeWidth=2;fontColor=#78350F;"
    card_ecs = card_base + "fillColor=#ECFEFF;strokeColor=#0891B2;strokeWidth=2;fontColor=#155E75;"
    card_forgerock = card_base + "fillColor=#F5F3FF;strokeColor=#6D28D9;strokeWidth=2;fontColor=#4C1D95;"
    card_aem = card_base + "fillColor=#FFF1F2;strokeColor=#BE123C;strokeWidth=2;fontColor=#881337;"
    card_sf = card_base + "fillColor=#F0F9FF;strokeColor=#0284C7;strokeWidth=2;fontColor=#0369A1;"
    card_sfmc = card_base + "fillColor=#FAF5FF;strokeColor=#7C3AED;strokeWidth=2;fontColor=#581C87;"
    card_abr = card_base + "fillColor=#ECFDF5;strokeColor=#047857;strokeWidth=2;fontColor=#064E3B;"
    card_gleif = card_base + "fillColor=#F0FDFA;strokeColor=#0D9488;strokeWidth=2;fontColor=#134E4A;"
    card_client = card_base + "fillColor=#0F172A;strokeColor=#334155;fontColor=#FFFFFF;"

    # 1. Title Banner & Legend
    b.add_box("AWS Enterprise Deployment Architecture with Native AWS Icons (North-to-South)\nDefense-in-Depth: Network Core, DMZ BFF, Internal EKS Microservices, On-Prem Direct Connect &amp; External SaaS/Registers", 
              60, 30, 2050, 85, title_style)
    
    legend_html = "<b>AWS ICON CATEGORIES &amp; INTEGRATIONS:</b><br>" \
                  "<span style='color:#8C4FFF; font-weight:bold;'>■ Networking:</span> API GW, ALB, NLB, TGW, DXGW&nbsp;&nbsp;|&nbsp;&nbsp;" \
                  "<span style='color:#ED7100; font-weight:bold;'>■ Compute:</span> EKS, Lambda&nbsp;&nbsp;|&nbsp;&nbsp;" \
                  "<span style='color:#7AA116; font-weight:bold;'>■ Storage:</span> S3 Bucket<br>" \
                  "<span style='color:#CC2264; font-weight:bold;'>■ Security:</span> KMS, GuardDuty, Cedar&nbsp;&nbsp;|&nbsp;&nbsp;" \
                  "<span style='color:#E7157B; font-weight:bold;'>■ Integration:</span> SQS, EventBridge&nbsp;&nbsp;|&nbsp;&nbsp;" \
                  "<span style='color:#2E27AD; font-weight:bold;'>■ Database:</span> RDS, RDS Proxy<br>" \
                  "<span style='color:#BE123C; font-weight:bold;'>― AEM SaaS</span>&nbsp;|&nbsp;" \
                  "<span style='color:#0891B2; font-weight:bold;'>― Dell ECS</span>&nbsp;|&nbsp;" \
                  "<span style='color:#6D28D9; font-weight:bold;'>― ForgeRock</span>&nbsp;|&nbsp;" \
                  "<span style='color:#1E3A8A; font-weight:bold;'>― nCore</span>&nbsp;|&nbsp;" \
                  "<span style='color:#B45309; font-weight:bold;'>― MAP/TIBCO</span>&nbsp;|&nbsp;" \
                  "<span style='color:#047857; font-weight:bold;'>― ABR</span>&nbsp;|&nbsp;" \
                  "<span style='color:#0284C7; font-weight:bold;'>― Salesforce</span>"
    b.add_box(legend_html, 2130, 30, 950, 85, legend_style)

    # 2. External Clients & Consumers Layer (Y: 145 to 225)
    c_web = b.add_aws_card("Web Browsers / End Users", 
                           ["HTTPS / TLS 1.3 (app.domain.com)", "NextJS SSR & Client Fetch"],
                           100, 145, 270, 75, "users", "#1E293B", card_client)

    c_b2b = b.add_aws_card("External API Clients / Partners",
                           ["B2B Direct REST Clients & Mobile", "API Keys & Bearer Tokens"],
                           410, 145, 270, 75, "users", "#1E293B", card_client)

    c_upload = b.add_aws_card("Document Upload Clients",
                             ["Web Forms & Partner Submissions", "Multipart Document Payloads"],
                             720, 145, 270, 75, "users", "#1E293B", card_client)
    
    c_sfmc_callback = b.add_aws_card("SFMC (Inbound Caller)",
                                    ["Email Status Delivery Webhook", "OAuth2 Client Credentials"],
                                    1030, 145, 340, 75, "simple_email_service", "#7C3AED", card_sfmc)

    # 3. Perimeter Cloud Edge (Imperva)
    edge_imperva = b.add_aws_card("Imperva Cloud Security Platform (CDN / Layer 7 WAF / Anti-DDoS)",
                                  ["Global Anycast Ingress, SSL Offload, Bot Mitigation, Rate Limiting & L7 Inspection"],
                                  100, 250, 1270, 65, "waf", "#BE185D", card_security)

    # 4. Network Account (Y: 345 to 655)
    acc_net = b.add_box("AWS Account: Network Core (account-network-prod)", 60, 345, 3020, 310, acc_network_style)
    vpc_net = b.add_box("Network VPC (vpc-network-central | 10.100.0.0/16)", 90, 390, 2960, 245, vpc_style, parent=acc_net)
    
    f5_in = b.add_aws_card("Inbound F5 BIG-IP Appliance Cluster",
                           ["SSL Offload & Re-encrypt, Ingress WAF", "Reverse Proxy to DMZ ALB & NLB"],
                           120, 445, 380, 85, "network_firewall", "#DC2626", card_security, parent=vpc_net)

    f5_out = b.add_aws_card("Outbound / Egress F5 BIG-IP Cluster",
                            ["Egress Forward Proxy, Deep Packet Inspection", "NAT Gateway to SaaS: AEM, ABR, GLEIF, SF"],
                            540, 445, 430, 85, "network_firewall", "#DC2626", card_security, parent=vpc_net)
    
    tgw = b.add_aws_card("AWS Transit Gateway (TGW) - Core Hub",
                         ["Multi-Account Hub: Network, DMZ, Internal, Kafka", "Centralized Private East-West Routing & ECMP"],
                         1020, 435, 840, 105, "transit_gateway", "#8C4FFF", card_network, parent=vpc_net)
    
    dxgw = b.add_aws_card("AWS Direct Connect Gateway (DXGW)",
                          ["Dual 10Gbps Dedicated DX Circuits to On-Prem DC", "Routes: Dell ECS, ForgeRock, MAP (TIBCO :9222), nCore"],
                          1920, 435, 640, 105, "direct_connect", "#8C4FFF", card_network, parent=vpc_net)

    # 5. DMZ Account (Y: 685 to 1425)
    acc_dmz = b.add_box("AWS Account: DMZ Ingress Boundary (account-dmz-prod)", 60, 685, 3020, 710, acc_dmz_style)
    
    # DMZ Account-Level Services (Serverless)
    band_dmz_acc = b.add_box("DMZ Account-Level Services (Decoupled Serverless &amp; Security Services)", 90, 730, 2960, 110, account_services_band, parent=acc_dmz)
    
    s3_dmz_temp = b.add_aws_card("S3 Bucket: DMZ Temp",
                                 ["s3://dmz-file-uploads-temp", "Lifecycle Expiry: 24 Hours"],
                                 120, 760, 260, 65, "s3", "#7AA116", card_storage, parent=band_dmz_acc)

    guardduty = b.add_aws_card("AWS GuardDuty Malware Scan",
                               ["S3 Malware Protection Engine", "Automated Threat Scanning"],
                               420, 760, 260, 65, "guardduty", "#ED7100", card_security, parent=band_dmz_acc)

    s3_dmz_quarantine = b.add_aws_card("S3 Bucket: Quarantine",
                                       ["s3://dmz-infected-quarantine", "KMS Deny Policy & SecOps Alert"],
                                       720, 760, 260, 65, "s3", "#E11D48", card_security, parent=band_dmz_acc)

    eb_dmz = b.add_aws_card("Amazon EventBridge (DMZ Bus)",
                            ["GuardDuty S3 Scan Results", "SFMC Ingestion Events"],
                            1020, 760, 320, 65, "eventbridge", "#E7157B", card_integration, parent=band_dmz_acc)

    # DMZ VPC
    vpc_dmz = b.add_box("DMZ VPC (vpc-dmz-external | 10.101.0.0/16)", 90, 855, 2960, 520, vpc_style, parent=acc_dmz)
    
    dmz_alb = b.add_aws_card("DMZ Internal ALB",
                             ["Listener: HTTPS 443", "Target: NextJS Pods in DMZ EKS"],
                             120, 915, 280, 75, "application_load_balancer", "#8C4FFF", card_network, parent=vpc_dmz)
    
    dmz_nlb_priv = b.add_aws_card("DMZ NLB / PrivateLink",
                                  ["PrivateLink from Inbound F5", "Target: DMZ API Gateway"],
                                  440, 915, 280, 75, "network_load_balancer", "#8C4FFF", card_network, parent=vpc_dmz)
    
    dmz_apigw = b.add_aws_card("AWS API Gateway (DMZ)",
                               ["[1] POST /v1/files/upload (Multipart)", "[2] POST /v1/notifications/sfmc-callback"],
                               760, 905, 540, 90, "api_gateway", "#8C4FFF", card_network, parent=vpc_dmz)
    
    dmz_auth_lambda = b.add_aws_card("DMZ Lambda Authorizer",
                                     ["Validates SFMC OAuth2 Client Credentials", "3-Way Auth: Auth Svc / JWKS / Cedar"],
                                     1340, 905, 430, 90, "lambda", "#ED7100", card_compute, parent=vpc_dmz)
    
    # DMZ Compute Tier
    dmz_eks = b.add_box("DMZ EKS Cluster (eks-dmz-frontend)", 120, 1025, 500, 210, cluster_style, parent=vpc_dmz)
    
    dmz_nextjs_pod = b.add_aws_card("Next.js App Pod (BFF)",
                                    ["Server-Side Rendering (SSR) & Web App", "Fetches Public Content from AEM SaaS", "Private backend calls to Internal API GW"],
                                    135, 1060, 470, 145, "eks", "#ED7100", card_compute, parent=dmz_eks)
    
    dmz_upload_lambda = b.add_aws_card("File Upload Lambda",
                                       ["Streams Payload to DMZ Temp S3", "Emits FileCreated Notification"],
                                       760, 1065, 320, 85, "lambda", "#ED7100", card_compute, parent=vpc_dmz)
    
    dmz_sfmc_handler = b.add_aws_card("SFMC Callback Lambda",
                                      ["Ingests SFMC Webhook Callback", "Publishes to EventBridge DMZ Bus"],
                                      1120, 1065, 340, 85, "lambda", "#ED7100", card_compute, parent=vpc_dmz)
    
    dmz_tgw_attach = b.add_aws_card("DMZ TGW Attachment",
                                    ["Private egress: Internal API GW & Outbound F5"],
                                    1500, 1065, 410, 85, "transit_gateway", "#8C4FFF", card_network, parent=vpc_dmz)

    # 6. Internal Core Account (Y: 1425 to 2585)
    acc_internal = b.add_box("AWS Account: Internal Core Business Services (account-internal-prod)", 60, 1425, 3020, 1140, acc_internal_style)
    
    # Internal Account-Level Services (Serverless)
    band_int_acc = b.add_box("Internal Account-Level Services (Serverless Eventing, Storage, SQS &amp; Cryptography)", 90, 1470, 2960, 110, account_services_band, parent=acc_internal)
    
    eb_internal = b.add_aws_card("Amazon EventBridge (Internal Bus)",
                                 ["Cross-Account Receiver from DMZ", "Rules: CleanFileScanned & SFMCCallback"],
                                 120, 1500, 360, 65, "eventbridge", "#E7157B", card_integration, parent=band_int_acc)

    lambda_s3_copy = b.add_aws_card("S3 Cross-Account Transfer Lambda",
                                    ["Triggered by Clean Scan Event", "Copies: DMZ Temp -> Internal S3"],
                                    520, 1500, 340, 65, "lambda", "#ED7100", card_compute, parent=band_int_acc)

    s3_int_clean = b.add_aws_card("S3 Bucket: Internal Archive",
                                  ["s3://internal-clean-documents-archive", "SSE-KMS Encrypted, PDF/A-2b Long-Term Store"],
                                  900, 1500, 420, 65, "s3", "#7AA116", card_storage, parent=band_int_acc)

    sqs_pdf = b.add_aws_card("Amazon SQS: PDF Queue",
                             ["pdf-generation-jobs.fifo", "Decoupled async buffer for PDF Workers"],
                             1360, 1500, 380, 65, "sqs", "#E7157B", card_integration, parent=band_int_acc)

    kms_key = b.add_aws_card("AWS KMS: Asymmetric Key",
                             ["RSA_2048 / ECC Key Pair for JWT Signing", "CloudHSM Private Key; Public Key to JWKS"],
                             1780, 1500, 400, 65, "kms", "#CC2264", card_security, parent=band_int_acc)

    # Internal VPC
    vpc_int = b.add_box("Internal VPC (vpc-internal-core | 10.102.0.0/16)", 90, 1595, 2960, 950, vpc_style, parent=acc_internal)
    
    # API Gateway & Authorizer Tier
    int_vpce_apigw = b.add_aws_card("Internal Private API Gateway",
                                    ["execute-api Interface VPC Endpoint", "Accessed privately via TGW from NextJS"],
                                    120, 1645, 480, 85, "api_gateway", "#8C4FFF", card_network, parent=vpc_int)

    int_auth_lambda = b.add_aws_card("Internal Lambda Authorizer",
                                     ["Calls Auth Svc / ForgeRock Proxy", "Validates JWKS & Evaluates Cedar"],
                                     640, 1645, 400, 85, "lambda", "#ED7100", card_compute, parent=vpc_int)

    lambda_jwks = b.add_aws_card("JWKS Endpoint Lambda",
                                 ["Exposes RFC 7517 Public Key JSON", "Validates signatures of presented JWTs"],
                                 1080, 1645, 340, 85, "lambda", "#ED7100", card_compute, parent=vpc_int)

    cedar_eval_svc = b.add_aws_card("Policy Evaluation Service",
                                    ["CEDAR Policy Engine (ABAC/RBAC)", "Validates Principal, Action, Resource"],
                                    1460, 1645, 360, 85, "shield", "#CC2264", card_security, parent=vpc_int)

    # Microservices: Internal EKS Cluster
    eks_int = b.add_box("Internal EKS Cluster (eks-internal-microservices)", 120, 1755, 1880, 460, cluster_style, parent=vpc_int)
    
    pod_submission = b.add_aws_card("Submission Service",
                                    ["Stores Submissions & Metadata", "Persists to RDS Postgres via Proxy"],
                                    140, 1805, 270, 75, "eks", "#ED7100", card_compute, parent=eks_int)

    pod_validation = b.add_aws_card("Validation Service",
                                    ["OPA (Open Policy Agent) Engine", "Rego Rule Evaluation & Schemas"],
                                    440, 1805, 270, 75, "eks", "#ED7100", card_compute, parent=eks_int)

    pod_sub_auth = b.add_aws_card("Submission Authorisation",
                                  ["Status Updates & Approvals", "Updates RDS Postgres Database"],
                                  740, 1805, 280, 75, "eks", "#ED7100", card_compute, parent=eks_int)

    pod_enrichment = b.add_aws_card("Enrichment Service",
                                    ["Payload Enrichment Orchestrator", "Calls RDS & Reference Data Lambdas"],
                                    1050, 1805, 280, 75, "eks", "#ED7100", card_compute, parent=eks_int)

    pod_pdf_gen = b.add_aws_card("PDF Generation Service",
                                 ["Hexagonal Java 21 / Spring Boot", "iText 8 + Thymeleaf -> PDF/A-2b", "Consumes SQS, writes to S3"],
                                 1360, 1805, 290, 95, "eks", "#ED7100", card_compute, parent=eks_int)
    
    pod_lodgement = b.add_aws_card("Lodgement Service",
                                   ["Triggers MAP Adaptor for XML", "Publishes to TIBCO EMS (:9222)", "Streams PDF -> Dell ECS S3 API"],
                                   1680, 1805, 280, 95, "eks", "#0891B2", card_ecs, parent=eks_int)

    # Pods Row 2
    pod_auth_svc = b.add_aws_card("Authorisation & Token Service",
                                  ["Proxies user auth to On-Prem ForgeRock", "Validates Directory Credentials via DXGW", "Mints JWT signed with KMS Asymmetric Key"],
                                  140, 1935, 285, 95, "eks", "#6D28D9", card_forgerock, parent=eks_int)
    
    pod_codeset = b.add_aws_card("CodeSet Lookup Service",
                                 ["Regulatory Codes & Values", "Direct RDS Postgres Query"],
                                 445, 1935, 270, 85, "eks", "#ED7100", card_compute, parent=eks_int)
    
    pod_ncore = b.add_aws_card("nCore Adaptor Service",
                               ["JSON <-> XML Bi-directional Translation", "Dispatches Core Banking REST API", "Connects to On-Prem nCore via DXGW"],
                               735, 1935, 285, 95, "eks", "#1E3A8A", card_ncore, parent=eks_int)
    
    pod_map = b.add_aws_card("MAP Adaptor Service",
                             ["JSON <-> XML Transformation Engine", "TIBCO EMS JMS/TCP Client Driver", "Publishes XML to Port 9222 via DXGW"],
                             1040, 1935, 285, 95, "eks", "#B45309", card_map, parent=eks_int)
    
    pod_notif = b.add_aws_card("Notification Service",
                               ["Stores & sends email alerts", "Updates status from SFMC callbacks", "Calls Salesforce & SFMC REST APIs"],
                               1345, 1935, 305, 95, "eks", "#ED7100", card_compute, parent=eks_int)
    
    pod_kafka_sub = b.add_aws_card("Kafka Subscriber Pod",
                                   ["Event Streaming Producer & Consumer", "TLS & SASL_SSL Authentication", "TCP Ports: 9092 / 9093 via TGW"],
                                   1670, 1935, 290, 95, "eks", "#EA580C", card_compute, parent=eks_int)

    # Reference Data Serverless Container
    ref_container = b.add_box("Reference Data Services (Serverless Lambdas via Internal API Gateway)", 2040, 1645, 960, 570, cluster_style, parent=vpc_int)
    
    l_issuer = b.add_aws_card("Issuer Service (Lambda)", ["REST API | Data from RDS Postgres"], 2070, 1695, 260, 65, "lambda", "#ED7100", card_compute, parent=ref_container)
    l_instr = b.add_aws_card("Instrument Service (Lambda)", ["REST API | Data from RDS Postgres"], 2360, 1695, 260, 65, "lambda", "#ED7100", card_compute, parent=ref_container)
    l_cal = b.add_aws_card("Calendar Service (Lambda)", ["REST API | Business Calendars from RDS"], 2650, 1695, 280, 65, "lambda", "#ED7100", card_compute, parent=ref_container)
    l_country = b.add_aws_card("Country Service (Lambda)", ["REST API | ISO Country Codes from RDS"], 2070, 1785, 260, 65, "lambda", "#ED7100", card_compute, parent=ref_container)
    l_curr = b.add_aws_card("Currency Service (Lambda)", ["REST API | Currency Codes & FX from RDS"], 2360, 1785, 260, 65, "lambda", "#ED7100", card_compute, parent=ref_container)
    
    l_org = b.add_aws_card("Organisation Service (Lambda)",
                           ["Reads Internal Org profiles from RDS Postgres", "External REST: ABR (Australian Business Register)", "External REST: GLEIF (Overseas Company LEI)", "External REST: Salesforce SaaS (CRM Org Data)"],
                           2070, 1875, 890, 110, "lambda", "#ED7100", card_compute, parent=ref_container)

    # Database Tier
    rds_proxy = b.add_aws_card("AWS RDS Proxy",
                               ["IAM Authentication & High Availability", "Connection Pooling for Lambdas & EKS Pods"],
                               400, 2245, 900, 70, "rds", "#2E27AD", card_database, parent=vpc_int)

    rds_db = b.add_aws_card("Amazon RDS PostgreSQL (Multi-AZ)",
                            ["Primary Master & Standby Replica | Encrypted Storage", "Submissions, Reference Data, Workflow Status & Codesets"],
                            1400, 2235, 750, 85, "rds", "#2E27AD", card_database, parent=vpc_int)

    # 7. External Integrations, Kafka & On-Premises Layer (Y: 2605 to 3350)
    
    # CONFLUENT KAFKA ACCOUNT
    acc_kafka = b.add_box("AWS Account: Confluent Kafka (account-kafka-prod)", 60, 2605, 580, 560, acc_kafka_style)
    vpc_kafka = b.add_box("Kafka VPC (vpc-kafka-cluster | 10.103.0.0/16)", 80, 2650, 540, 495, vpc_style, parent=acc_kafka)
    
    kafka_brokers = b.add_aws_card("Confluent Kafka Enterprise Cluster",
                                   ["Broker Ports: TCP 9092 / 9093 (TLS / SASL)", "Schema Registry: Port 8081 (Avro/JSON)", "Multi-AZ KRaft / Zookeeper Quorum", "AWS Transit Gateway Cross-Account Route"],
                                   100, 2705, 500, 125, "managed_streaming_for_kafka", "#EA580C", card_compute, parent=vpc_kafka)

    # On-Premises Data Center (via Direct Connect)
    acc_onprem = b.add_box("On-Premises Corporate Data Center (Connected via AWS Direct Connect Gateway / 802.1Q Trunk)", 680, 2605, 1220, 560, acc_onprem_style)
    
    onprem_forgerock = b.add_aws_card("On-Premise ForgeRock Instance (OpenAM)",
                                      ["Enterprise Identity & Access Management (IAM)", "Enterprise LDAP / User Credential Store", "HTTPS REST / OpenAM Identity API via DXGW"],
                                      710, 2675, 275, 115, "traditional_server", "#6D28D9", card_forgerock, parent=acc_onprem)
    
    onprem_tibco = b.add_aws_card("TIBCO EMS Message Broker (On-Premises)",
                                  ["Queue Port: TCP 9222", "Enterprise XML Transaction Messaging Queue", "Message Producer: MAP Adaptor Service via DXGW"],
                                  1005, 2675, 275, 115, "sqs", "#B45309", card_map, parent=acc_onprem)
    
    onprem_dell_ecs = b.add_aws_card("Dell ECS Object Storage (On-Premises)",
                                     ["On-Premise Long-Term Regulatory PDF Archive", "Protocol: S3 REST API (s3:PutObject)", "Destination: On-Prem Dell ECS Storage Volume"],
                                     1300, 2675, 280, 115, "s3", "#0891B2", card_ecs, parent=acc_onprem)
    
    onprem_ncore = b.add_aws_card("nCore Banking Instance (On-Premise Core)",
                                  ["Core Banking Ledger & Financial Settlement", "On-Premise nCore XML REST API", "XML Payload (translated by nCore Adaptor)"],
                                  1595, 2675, 285, 115, "traditional_server", "#1E3A8A", card_ncore, parent=acc_onprem)

    # External SaaS & Third-Party APIs
    acc_saas = b.add_box("External SaaS, CMS &amp; Government Registers (Egress via Outbound F5 / NAT)", 1940, 2605, 1140, 660, acc_saas_style)
    
    saas_abr = b.add_aws_card("ABR (Australian Business Register)",
                              ["abr.business.gov.au/abrxmlsearch/", "ABN Lookup, Legal Type, GST Status, ASIC ACN", "Auth: ABR GUID / API Key over TLS 1.3"],
                              1970, 2665, 520, 100, "certificate_manager", "#047857", card_abr, parent=acc_saas)
    
    saas_gleif = b.add_aws_card("GLEIF (Global Legal Entity Identifier)",
                                ["api.gleif.org/api/v1/lei-records", "Overseas Entity Verification, ISO 17442 LEI Codes", "Bearer / API Token over HTTPS TLS 1.3"],
                                2520, 2665, 530, 100, "global_accelerator", "#0D9488", card_gleif, parent=acc_saas)

    saas_sf = b.add_aws_card("Salesforce SaaS (Core CRM Cloud)",
                             ["[1] Org/Account Profiles (from Org Service)", "[2] Email Activity Logs (from Notif Service)", "Protocol: HTTPS / TLS 1.3 REST API"],
                             1970, 2785, 520, 95, "users", "#0284C7", card_sf, parent=acc_saas)
    
    saas_sfmc = b.add_aws_card("Salesforce Marketing Cloud (SFMC)",
                               ["[1] Outbound Email Dispatch API (from Notif)", "[2] Inbound Status Callbacks (to DMZ API GW)", "Protocol: HTTPS / TLS 1.3 REST API"],
                               2520, 2785, 530, 95, "simple_email_service", "#7C3AED", card_sfmc, parent=acc_saas)

    saas_aem = b.add_aws_card("Adobe Experience Manager (AEM SaaS)",
                              ["Enterprise Headless CMS, DAM & Public Content", "Consumer: Next.js SSR & BFF App Pod (DMZ EKS)", "GraphQL Delivery API / Experience Fragments", "HTTPS TLS 1.3 (Egress via Outbound F5 & NAT)"],
                              1970, 2900, 1080, 105, "cloudfront", "#BE123C", card_aem, parent=acc_saas)

    # ------------------ CONNECTORS / FLOWS ------------------

    # Ingress Client Flows (Blue)
    flow_ingress = "strokeColor=#2563EB;strokeWidth=2;"
    b.add_edge(c_web, edge_imperva, "HTTPS / 443", flow_ingress)
    b.add_edge(c_b2b, edge_imperva, "HTTPS / 443", flow_ingress)
    b.add_edge(c_upload, edge_imperva, "POST /files", flow_ingress)
    
    # SFMC Inbound Webhook Link
    flow_sfmc = "strokeColor=#7C3AED;strokeWidth=2.5;"
    b.add_edge(c_sfmc_callback, edge_imperva, "Inbound Email Callbacks (OAuth2)", flow_sfmc)
    
    b.add_edge(edge_imperva, f5_in, "Screened HTTPS Traffic", flow_ingress)

    # F5 Inbound Routing
    b.add_edge(f5_in, dmz_alb, "Web Traffic (Port 443)", flow_ingress)
    b.add_edge(f5_in, dmz_nlb_priv, "API & SFMC Callbacks", flow_ingress)
    b.add_edge(dmz_nlb_priv, dmz_apigw, "PrivateLink Ingress", flow_ingress)
    b.add_edge(dmz_alb, dmz_nextjs_pod, "Reverse Proxy to Pod (443)", flow_ingress)

    # DMZ API Gateway Handlers
    b.add_edge(dmz_apigw, dmz_auth_lambda, "Validate OAuth2 / Auth", "strokeColor=#7C3AED;strokeWidth=2;")
    b.add_edge(dmz_apigw, dmz_upload_lambda, "Stream File Payload", flow_ingress)
    b.add_edge(dmz_apigw, dmz_sfmc_handler, "Forward SFMC Callback", flow_sfmc)
    b.add_edge(dmz_sfmc_handler, eb_dmz, "Publish 'SFMCCallbackReceived'", flow_sfmc)

    # File Upload & GuardDuty Flow
    b.add_edge(dmz_upload_lambda, s3_dmz_temp, "1. s3:PutObject (Temp)", "strokeColor=#10B981;strokeWidth=2;")
    b.add_edge(guardduty, s3_dmz_temp, "2. Malware Scan Event", "strokeColor=#BE185D;strokeWidth=2;dashed=1;")
    b.add_edge(guardduty, eb_dmz, "3. Emit ScanResult Event", "strokeColor=#EC4899;strokeWidth=2;")
    b.add_edge(eb_dmz, s3_dmz_quarantine, "Branch: Infected -> Quarantine", "strokeColor=#DC2626;strokeWidth=2;dashed=1;")
    b.add_edge(eb_dmz, eb_internal, "Cross-Account Events (Clean File / SFMC Callback)", "strokeColor=#059669;strokeWidth=2.5;dashed=1;")
    b.add_edge(eb_internal, lambda_s3_copy, "Trigger Clean Transfer", "strokeColor=#059669;strokeWidth=2;")
    b.add_edge(lambda_s3_copy, s3_int_clean, "s3:CopyObject (Cross-Account)", "strokeColor=#059669;strokeWidth=2;")

    # NextJS BFF to Internal API Gateway via TGW
    flow_tgw = "strokeColor=#059669;strokeWidth=2.5;"
    b.add_edge(dmz_nextjs_pod, dmz_tgw_attach, "BFF Backend Requests", flow_tgw)
    b.add_edge(dmz_tgw_attach, tgw, "Private Interconnect (TGW)", flow_tgw)
    b.add_edge(tgw, int_vpce_apigw, "Route to execute-api VPCE", flow_tgw)

    # AEM SaaS Public Content Flow (Adobe Crimson #BE123C)
    flow_aem = "strokeColor=#BE123C;strokeWidth=3;"
    b.add_edge(dmz_nextjs_pod, tgw, "1. Fetch AEM Public Content via TGW", flow_aem)
    b.add_edge(tgw, f5_out, "2. Route AEM Egress to F5", flow_aem)
    b.add_edge(f5_out, saas_aem, "3. HTTPS GraphQL: AEM SaaS Content Delivery API", flow_aem)

    # Internal API Gateway & Authorizer Flows
    b.add_edge(int_vpce_apigw, int_auth_lambda, "Authorize Request", "strokeColor=#7C3AED;strokeWidth=2;")
    b.add_edge(int_auth_lambda, pod_auth_svc, "1. Authenticate (ForgeRock Proxy)", "strokeColor=#6D28D9;strokeWidth=2.5;")
    b.add_edge(int_auth_lambda, lambda_jwks, "2. Validate JWT Signature", "strokeColor=#7C3AED;strokeWidth=2;")
    b.add_edge(int_auth_lambda, cedar_eval_svc, "3. Evaluate Cedar Policy", "strokeColor=#7C3AED;strokeWidth=2;")

    # DMZ Authorizer to Internal Security Services
    b.add_edge(dmz_auth_lambda, tgw, "Auth Proxy / Cedar Validation", "strokeColor=#7C3AED;strokeWidth=1.5;dashed=1;")

    # ForgeRock & KMS Token Minting Flow (Royal Purple #6D28D9)
    flow_forgerock = "strokeColor=#6D28D9;strokeWidth=3;"
    b.add_edge(pod_auth_svc, tgw, "1. Proxy Auth Request via TGW", flow_forgerock)
    b.add_edge(tgw, dxgw, "Route ForgeRock via DXGW Trunk", flow_forgerock)
    b.add_edge(dxgw, onprem_forgerock, "2. HTTPS REST / OpenAM: Validate User Credentials", flow_forgerock)
    b.add_edge(pod_auth_svc, kms_key, "3. Mint & Sign JWT (Asymmetric CloudHSM Key)", flow_forgerock)
    b.add_edge(lambda_jwks, kms_key, "Expose KMS Public Key (RFC 7517 JWKS)", "strokeColor=#7C3AED;strokeWidth=2;")

    # Internal API Gateway to EKS Microservices & Reference Data Lambdas
    b.add_edge(int_vpce_apigw, pod_submission, "Route /submissions", flow_tgw)
    b.add_edge(int_vpce_apigw, pod_codeset, "Route /codesets", flow_tgw)
    b.add_edge(int_vpce_apigw, pod_ncore, "Route /ncore/transactions", flow_tgw)
    b.add_edge(int_vpce_apigw, l_issuer, "Route /issuers", flow_tgw)
    b.add_edge(int_vpce_apigw, l_instr, "Route /instruments", flow_tgw)
    b.add_edge(int_vpce_apigw, l_cal, "Route /calendars", flow_tgw)
    b.add_edge(int_vpce_apigw, l_org, "Route /organisations", flow_tgw)

    # EventBridge to Notification Service
    b.add_edge(eb_internal, pod_notif, "Deliver SFMC Callback Status", flow_sfmc)

    # Core EKS Pod Workflows
    b.add_edge(pod_submission, pod_validation, "Validate Payload (OPA/Rego)", "strokeColor=#2563EB;strokeWidth=2;")
    b.add_edge(pod_submission, pod_sub_auth, "Update Status", "strokeColor=#2563EB;strokeWidth=2;")
    b.add_edge(pod_submission, pod_enrichment, "Trigger Enrichment", "strokeColor=#2563EB;strokeWidth=2;")
    b.add_edge(pod_submission, sqs_pdf, "Async PDF Request (202 Accepted)", "strokeColor=#F59E0B;strokeWidth=2.5;")
    
    # PDF Generation Service
    b.add_edge(sqs_pdf, pod_pdf_gen, "Consume PDF Job", "strokeColor=#F59E0B;strokeWidth=2;")
    b.add_edge(pod_pdf_gen, s3_int_clean, "Store Generated PDF/A-2b", "strokeColor=#10B981;strokeWidth=2;")
    
    # Lodgement & MAP Adaptor Flows
    flow_map = "strokeColor=#B45309;strokeWidth=3;"
    b.add_edge(pod_lodgement, pod_map, "1. Handover Lodgement (JSON Payload)", flow_map)
    b.add_edge(pod_lodgement, s3_int_clean, "2. Fetch PDF from S3", "strokeColor=#10B981;strokeWidth=1.5;dashed=1;")

    # Dell ECS S3 Flow
    flow_ecs = "strokeColor=#0891B2;strokeWidth=3;"
    b.add_edge(pod_lodgement, tgw, "3. S3 API: Stream PDF to Dell ECS via TGW", flow_ecs)
    b.add_edge(tgw, dxgw, "Route Dell ECS S3 Traffic via DXGW Trunk", flow_ecs)
    b.add_edge(dxgw, onprem_dell_ecs, "S3 Protocol (HTTPS): Dell ECS Storage Volume", flow_ecs)

    # MAP Adaptor to TIBCO EMS via TGW & DXGW
    b.add_edge(pod_map, tgw, "Publish XML Message (Port 9222 via TGW)", flow_map)
    b.add_edge(tgw, dxgw, "Route TIBCO Port 9222 via DXGW Trunk", flow_map)
    b.add_edge(dxgw, onprem_tibco, "TCP Port 9222: On-Prem TIBCO EMS Queue", flow_map)

    # nCore On-Premise Flow
    flow_ncore = "strokeColor=#1E3A8A;strokeWidth=3;"
    b.add_edge(pod_ncore, tgw, "nCore XML Settlement via TGW", flow_ncore)
    b.add_edge(tgw, dxgw, "Route nCore via DXGW Trunk", flow_ncore)
    b.add_edge(dxgw, onprem_ncore, "HTTPS REST (XML): On-Prem nCore Banking API", flow_ncore)

    # Confluent Kafka Flow
    flow_kafka = "strokeColor=#EA580C;strokeWidth=3;"
    b.add_edge(pod_kafka_sub, tgw, "Kafka TCP Wire Protocol (Ports 9092/9093 via TGW)", flow_kafka)
    b.add_edge(tgw, kafka_brokers, "Cross-Account TGW Route (Kafka VPC: 10.103.0.0/16)", flow_kafka)

    # Database Access via RDS Proxy
    flow_db = "strokeColor=#0D9488;strokeWidth=2;"
    b.add_edge(pod_submission, rds_proxy, "Store Submissions", flow_db)
    b.add_edge(pod_sub_auth, rds_proxy, "Status Updates", flow_db)
    b.add_edge(pod_enrichment, rds_proxy, "Reference Data", flow_db)
    b.add_edge(pod_codeset, rds_proxy, "Lookup Codes", flow_db)
    b.add_edge(l_issuer, rds_proxy, "Query Issuers", flow_db)
    b.add_edge(l_instr, rds_proxy, "Query Instruments", flow_db)
    b.add_edge(l_cal, rds_proxy, "Query Calendars", flow_db)
    b.add_edge(l_country, rds_proxy, "Query Countries", flow_db)
    b.add_edge(l_curr, rds_proxy, "Query Currencies", flow_db)
    b.add_edge(l_org, rds_proxy, "Query Internal Orgs", flow_db)
    b.add_edge(rds_proxy, rds_db, "Pooled DB Connections (IAM Auth)", flow_db)

    # External Registers & SaaS Links
    flow_abr = "strokeColor=#047857;strokeWidth=3;"
    b.add_edge(l_org, tgw, "ABR ABN Validation Request via TGW", flow_abr)
    b.add_edge(tgw, f5_out, "Route ABR Egress Traffic", flow_abr)
    b.add_edge(f5_out, saas_abr, "HTTPS REST: SearchByABN / Validate Entity", flow_abr)

    flow_gleif = "strokeColor=#0D9488;strokeWidth=3;"
    b.add_edge(l_org, tgw, "GLEIF Overseas LEI Request via TGW", flow_gleif)
    b.add_edge(tgw, f5_out, "Route GLEIF Egress Traffic", flow_gleif)
    b.add_edge(f5_out, saas_gleif, "HTTPS REST: Validate LEI Records (api.gleif.org)", flow_gleif)

    flow_sf = "strokeColor=#0284C7;strokeWidth=2.5;"
    b.add_edge(l_org, tgw, "Query Org/Accounts via TGW", flow_sf)
    b.add_edge(pod_notif, tgw, "Store & Log Email Audit via TGW", flow_sf)
    b.add_edge(f5_out, saas_sf, "Salesforce SaaS REST API (Org & Audit)", flow_sf)

    b.add_edge(pod_notif, tgw, "Dispatch Transactional Email via TGW", flow_sfmc)
    b.add_edge(f5_out, saas_sfmc, "SFMC Transactional Email REST API", flow_sfmc)

    return b.to_xml()

if __name__ == "__main__":
    xml_content = build_diagram()
    out_file = "/Users/gary/Documents/Repos/pdf-service/aws_deployment_architecture.drawio"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"Generated draw.io diagram successfully at: {out_file}")
