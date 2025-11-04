module.exports = {
    "100": {
        description: "Happy path",
        "sendMessage": {
            "statusCode": 200,
            "body": {
                "summary": "Based on the information provided in the policy manual, a family of 4 may be eligible for SNAP benefits, but eligibility depends on several factors including income and resources. The policy states that 'An AU whose income is at or below the income limit is eligible to receive a benefit amount based on AU size and countable net income.' However, specific income limits for a family of 4 are not provided in the given context. The eligibility also depends on whether the household meets other criteria, such as not being disqualified for certain reasons (e.g., containing an IPV disqualified member, having a convicted drug felon, etc.).",
                "reasoning": [
                  {
                    "message": "'An AU whose income is at or below the income limit is eligible to receive a benefit amount based on AU size and countable net income.'",
                    "references": "SNAP Policy Manual, Income Limits and Benefit Levels section",
                    "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/3400/#income-limits-and-benefit-levels"
                  },
                  {
                    "message": "'A household is not considered categorically eligible if: It contains an IPV disqualified member. It has a member who is a convicted drug felon. The head of household is work sanctioned.'",
                    "references": "SNAP Policy Manual, Households Not Eligible for Categorical Eligibility section",
                    "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/3210/#households-not-eligible-for-categorical-eligibility"
                  }
                ],
                "references": [
                  {
                    "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/3400/#income-limits-and-benefit-levels",
                    "message": "This link provides information about income limits and benefit levels for SNAP eligibility."
                  },
                  {
                    "url": "https://gadhs.gitlab.io/pamms/dfcs/snap/3210/#households-not-eligible-for-categorical-eligibility",
                    "message": "This link provides information about households that are not eligible for categorical eligibility in the SNAP program."
                  }
                ],
                "suggested": [
                    "d","f",
                  "What are the specific income limits for a family of 4 to be eligible for SNAP benefits?",
                  "How does the SNAP program calculate countable net income?",
                  "What are the resource limits for SNAP eligibility?",
                  "Are there any special considerations for families with elderly or disabled members?"
                ]
              }
        },
        "feedback": {
            "statusCode": 200,
        },
        "timeout": {
            "statusCode": 200,
        },
        "extendSession": {
            "statusCode": 200,
        }
    },
    "101": {
        description: "PII/PHI",
        "sendMessage": {
            "statusCode": 400,
            "body": "PII/PHI Detected in the prompt, please remove the concerning elements from the prompt and try again."
        }
    },
    "102": {
        description: "No Prompt Provided",
        "sendMessage": {
            "statusCode": 400,
            "body": "No Prompt Provided"
        }
    },
    "103": {
        description: "No event received",
        "sendMessage": {
            "statusCode": 400,
            "body": "No event received"
        }
    },
    "104": {
        description: "Irrelevant Questions",
        "sendMessage": {
            "statusCode": 400,
            "body": "Irrelevant questions, no answers found"
        }
    },
    "105": {
        description: "Server is busy",
        "sendMessage": {
            "statusCode": 429,
            "body": "Too Many Requests"
        }
    },
    "106": {
        description: "Service Unavailable",
        "sendMessage": {
            "statusCode": 503,
            "body": "Service Unavailable"
        }
    },
    "107": {
        description: "Maintenance",
        "sendMessage": {
            "statusCode": 503,
            "body": "Service is down for maintenance from 09/25/2024 to 09/28/2024"
        }
    },
    "108": {
        description: "Gateway Timeout",
        "sendMessage": {
            "statusCode": 504,
            "body": "Gateway Timeout"
        }
    },
    "109": {
        description: "Other sendMessage errors",
        "sendMessage": {
            "statusCode": 520,
            "body": "Gateway Timeout"
        }
    },
    "110": {
        description: "Timeout",
        "sendMessage": {
            "statusCode": 520,
            "body": "Gateway Timeout",
            'responseTime': 30000,
        }
    },
    "201": {
        description: "Feedback errors",
        "feedback": {
            "statusCode": 503,
        }
    },
    "301": {
        description: "Timeout - errors",
        "sendMessage": {
            "statusCode": 520,
            "body": "Gateway Timeout",
            'responseTime': 30000,
        },
        "timeout": {
            "statusCode": 503,
        }
    },
    "401": {
        description: "Extend Session - Session not found.",
        "extendSession": {
            "statusCode": 404,
        }
    },
    "402": {
        description: "Extend Session - Other errors.",
        "extendSession": {
            "statusCode": 500,
        }
    },
}