import re
from flask import Flask, render_template, request

app = Flask(__name__)


def detect_environment(message: str) -> str:
    """Try to detect environment like PROD, UAT, DEV from square brackets or words."""
    msg_upper = message.upper()
    # First, check bracket style: [PROD], [DEV], [UAT], etc.
    env_match = re.search(r'\[(PROD|UAT|DEV|STAGE|TEST)\]', msg_upper)
    if env_match:
        return env_match.group(1).title()

    # Then, look for common patterns in plain text
    if " DEV " in msg_upper or "DEV-" in msg_upper or msg_upper.startswith("DEV "):
        return "Dev"
    if " PROD " in msg_upper or "PROD-" in msg_upper or msg_upper.startswith("PROD "):
        return "Prod"
    if " UAT " in msg_upper or "UAT-" in msg_upper or msg_upper.startswith("UAT "):
        return "Uat"
    if " STAGE " in msg_upper or "STAGE-" in msg_upper:
        return "Stage"
    if " TEST " in msg_upper or "TEST-" in msg_upper:
        return "Test"

    return "Unknown"



def analyze_trigger(message: str) -> dict:
    """Analyze a trigger message and return category, meaning, and action."""
    msg_upper = message.upper()

    # Default response
    result = {
        "category": "Uncategorized",
        "meaning": "No specific rule matched this alert message.",
        "recommended_action": (
            "Read the full alert, check which service or resource is mentioned, "
            "and share it with the DevOps team along with timestamp and screenshot."
        ),
        "environment": detect_environment(message)
    }
def analyze_trigger(message: str) -> dict:
    """Analyze a trigger message and return category, meaning, and action."""
    msg_upper = message.upper()
    if re.search(r'ISSUE\s*ID', msg_upper):
        result["category"] = "Diagnostic Issue"
        result["meaning"] = (
            "This alert refers to a specific Issue ID, indicating a tracked "
            "application-level or system-level problem."
        )
        result["recommended_action"] = (
            "Inform DevOps that a diagnostic alert with an Issue ID has fired. "
            "Share the Issue ID, full error message, timestamp, and attach a screenshot."
        )
    # Default response
    result = {
        "category": "Uncategorized",
        "meaning": "No specific rule matched this alert message.",
        "recommended_action": (
            "Read the full alert, check which service or resource is mentioned, "
            "and share it with the DevOps team along with timestamp and screenshot."
        ),
        "environment": detect_environment(message)
    }
        # NEW RULE: Docker / container / Kubernetes related alerts
    if (
        "DOCKER" in msg_upper
        or "CONTAINER" in msg_upper
        or "CONTAINER INSTANCE" in msg_upper
        or "KUBERNETES" in msg_upper
        or "K8S" in msg_upper
        or "POD " in msg_upper
        or "CONTAINER CPU" in msg_upper
        or "CONTAINER MEMORY" in msg_upper
        or "ECS" in msg_upper
    ):
        result["category"] = "Infrastructure Issue"
        result["meaning"] = (
            "This alert is related to a containerized workload (Docker/Kubernetes). "
            "It usually indicates issues with the container health, resource usage, "
            "or availability of the container or pod."
        )
        result["recommended_action"] = (
            "Inform DevOps that a container-related infrastructure alert has fired. "
            "Share the container/pod name, node or host if mentioned, severity, "
            "and attach a screenshot from the monitoring tool."
        )
        # 👇 Force all container alerts to be treated as Prod env
        result["environment"] = "Prod"
        return result

    # ---- RULES SECTION ----

    # 🔹 NEW RULE: Azure App Gateway / AppGw health alerts
    if "ISSUE ID" in msg_upper:
        result["category"] = "Diagnostic Issue"
        result["meaning"] = (
            "This alert refers to an Issue ID, usually indicating an application-level "
            "error or a specific tracked issue related to system functionality."
        )
        result["recommended_action"] = (
            "Inform DevOps that a diagnostic alert with an Issue ID has fired. "
            "Share the Issue ID, error message, timestamp, and attach a screenshot."
        )
    if "HOST" in msg_upper:
        result["category"] = "Infrastructure Issue"
        result["meaning"] = (
            "This alert indicates a host-level issue. Hosts typically refer to the "
            "underlying machine, VM, or node where your services or containers run."
        )
        result["recommended_action"] = (
            "Inform DevOps that a host-level infrastructure alert has fired. "
            "Share the host name, severity, and attach a screenshot from the monitoring tool."
        )
    if (
        "APPGW" in msg_upper
        or "APPLICATION GATEWAY" in msg_upper
        or "APP GATEWAY" in msg_upper
        or "MICROSOFT.NETWORK/APPLICATIONGATEWAYS" in msg_upper
    ):
        result["category"] = "Infrastructure Issue"
        result["meaning"] = (
            "This is a health alert for an Azure Application Gateway (AppGw). "
            "It usually indicates issues with backend health, routing, or gateway availability."
        )
        result["recommended_action"] = (
            "Inform DevOps that an Azure Application Gateway health alert has fired. "
            "Share the gateway name (e.g., dev-app-gateway), severity (Sev2), "
            "timestamp of the alert, and attach a screenshot from Azure Monitor."
        )
        return result

    # 1. High IOPS / DB related
    if "IOPS" in msg_upper:
        result["category"] = "Infrastructure Issue"
        result["meaning"] = (
            "High IOPS means the disk is doing too many read/write operations. "
            "Often related to database or storage load."
        )
        result["recommended_action"] = (
            "Inform DevOps that High IOPS is observed. Include database/instance name, "
            "time of alert, and attach screenshot of the alert."
        )
        return result

    # 2. High Error Count (APM)
    if "HIGH ERROR COUNT" in msg_upper:
        result["category"] = "Diagnostic Issue"
        result["meaning"] = (
            "The application is generating a large number of errors in a short time."
        )
        result["recommended_action"] = (
            "Inform DevOps that High Error Count is observed in the APM tool for this service. "
            "Attach sample error message, service name, and timeframe of the alert."
        )
        return result

    # ... keep the rest of your existing rules the same ...

    # ---- RULES SECTION ----

    # 1. High IOPS / DB related
    if "IOPS" in msg_upper:
        result["category"] = "Infrastructure Issue"
        result["meaning"] = (
            "High IOPS means the disk is doing too many read/write operations. "
            "Often related to database or storage load."
        )
        result["recommended_action"] = (
            "Inform DevOps that High IOPS is observed. Include database/instance name, "
            "time of alert, and attach screenshot of the alert."
        )
        return result

    # 2. High Error Count (APM)
    if "HIGH ERROR COUNT" in msg_upper:
        result["category"] = "Diagnostic Issue"
        result["meaning"] = (
            "The application is generating a large number of errors in a short time."
        )
        result["recommended_action"] = (
            "Inform DevOps that High Error Count is observed in the APM tool for this service. "
            "Attach sample error message, service name, and timeframe of the alert."
        )
        return result

    # 3. CPU related alerts
    if "CPU" in msg_upper and ("HIGH" in msg_upper or "SPIKE" in msg_upper or "UTILIZATION" in msg_upper):
        result["category"] = "Infrastructure Issue"
        result["meaning"] = "CPU usage on the server or instance is very high."
        result["recommended_action"] = (
            "Inform DevOps that high CPU utilization is observed on the mentioned instance. "
            "Share instance name, CPU percentage if shown, and screenshot."
        )
        return result

    # 4. Memory / RAM alerts
    if "MEMORY" in msg_upper or "RAM" in msg_upper:
        result["category"] = "Infrastructure Issue"
        result["meaning"] = "The server or application is using a high amount of memory."
        result["recommended_action"] = (
            "Inform DevOps that high memory usage is observed. Include instance name "
            "and attach screenshot of the alert."
        )
        return result

    # 5. Disk space alerts
    if "DISK" in msg_upper or "STORAGE" in msg_upper or "SPACE" in msg_upper:
        result["category"] = "Infrastructure Issue"
        result["meaning"] = "Disk/storage might be close to full or under pressure."
        result["recommended_action"] = (
            "Inform DevOps that disk/storage alert is observed. Share which disk/volume, "
            "percentage used if available, and screenshot."
        )
        return result

    # 6. Availability / Down / Unreachable
    if any(word in msg_upper for word in ["DOWN", "UNREACHABLE", "UNAVAILABLE", "TIMEOUT"]):
        result["category"] = "Diagnostic Issue"
        result["meaning"] = "The application or service might be down or not responding."
        result["recommended_action"] = (
            "Inform DevOps that the service appears down/unreachable. "
            "Mention service name, exact wording of the alert, and attach screenshot."
        )
        return result

    # 7. Intelligent Search / Query related (example)
    if "SEARCH" in msg_upper or "QUERY" in msg_upper:
        result["category"] = "Intelligent Search Issue"
        result["meaning"] = "There may be an issue with the search or query functionality."
        result["recommended_action"] = (
            "Inform DevOps that a search/query-related alert is triggered. "
            "If possible, note which index or query is mentioned and attach screenshot."
        )
        return result

    return result


@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    message = ""

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if message:
            analysis = analyze_trigger(message)

    return render_template("index.html", analysis=analysis, message=message)


if __name__ == "__main__":
    app.run(debug=True)
