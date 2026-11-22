# ALICE: legal notice and disclaimer

**Last updated:** November 16, 2026

**ALICE** is an **open source** post exploitation project for **cyber security professionals**. What follows supplements the repository `LICENSE` regarding limitation of liability.

---

## Software license

Reproduction, modification, and redistribution of the code are governed solely by the repository `LICENSE`. Armory modules and other dependencies have their own licenses, as stated in their respective `LICENSE` files.

---

## Purpose

The Software was designed to **simulate real attacks and threats** in **authorized** security exercises: reproduce adversary tactics after initial compromise, test vulnerabilities and exploitation paths, validate defensive controls, and measure detection and response capability (red team, purple team, pentest, audit, or lab research), always with permission from whoever is responsible for the systems, networks, and data involved.

It is not a consumer product nor a tool for unauthorized access to third party systems.

---

## Author position on illicit use

The Author **condemns and does not support** any illicit use of ALICE. The Author **does not** authorize, **does not** encourage, **does not** supervise, and **does not** take part in operations carried out by third parties with the Software.

ALICE is **not** intended for creating, distributing, or operating **malware** to attack third parties. Artifacts produced by anyone who misuses the Software for that purpose (implants, payloads, or tools for malicious use) **do not** represent the purpose of the project nor have the Author's support. Responsibility for that conduct lies solely with whoever engages in it.

---

## Third-party platforms and external C2

ALICE can route implant traffic through an **external C2** channel that the operator configures. That channel may be a service the operator reaches through **their own** API credentials. Mentions of **Telegram**, **Discord**, **Dropbox**, and similar names in the README, documentation, or source are **illustrative references only**: examples of third-party platforms that expose an API. They describe a class of possible transports. They are not a recommendation, an instruction, or permission to use those services.

The Author:

- **does not** endorse, encourage, or support use of any third-party platform **without authorization**, whether that authorization is missing from the owner of the systems under test or forbidden by the platform itself;
- **does not** operate, host, monitor, or control accounts, bots, tokens, API keys, or traffic on Telegram, Discord, Dropbox, or any other third-party service;
- **does not** supply credentials or infrastructure on those platforms. Anything of that kind is brought solely by the operator;
- **has no** partnership, sponsorship, agency, or affiliation with the owners of those platforms. Names and trademarks belong to their respective owners and are used only to identify the kind of service an operator might connect.

External C2 is a **transport option for authorized security work** (red team, purple team, pentest, audit, or lab), under permission from whoever is responsible for the systems, networks, and data in scope. It is **not** support for malware command-and-control, unauthorized access, fraud, or any other offense carried out through a consumer or cloud platform.

Before enabling any external channel, the operator must **both**:

1. hold **explicit authorization** covering the engagement and the systems in scope; and
2. comply with the **terms of service, acceptable use policy, developer policy, and applicable law** of every third-party platform involved.

If a platform prohibits automated abuse, covert command channels, malware distribution, or this kind of integration, the operator **must not** use it that way. A reference in this project **does not** override that platform's rules and **does not** permit use the platform has not allowed.

The Author **condemns** use of ALICE together with any third-party platform for unauthorized activity or for activity that platform does not allow. Account suspension, abuse reports, cooperation with authorities, and any other consequence of that conduct are the **operator's alone**. That conduct creates **no** agency, representation, or joint participation with the Author. To the fullest extent permitted by applicable law, the Author is **not liable** for how an operator uses, misuses, or connects third-party platforms through the Software.

---

## Limitation of liability

Anyone who uses, modifies, or redistributes ALICE assumes **full and exclusive responsibility** for their actions, for the legality of their operations, for any required authorizations, and for all effects arising from them, including toward third parties and authorities, in civil, administrative, and criminal matters. Anyone who uses the Software for unlawful conduct (such as unauthorized access, causing damage, exfiltrating data, extortion, fraud, or any other offense) is liable **on their own**, with no agency, representation, or joint participation with the Author.

To the **fullest extent permitted by applicable law**, the Author **is not liable** for any losses, damages, obligations, claims, or consequences of any kind related to the Software, its use, misuse, unavailability, or integration with other tools, **even if warned** of the possibility. Any liability of the Author that the law does not allow to exclude is limited to the **minimum legally required**, except in cases of **intentional misconduct** by the Author.

---

*Informational document. Rights to the code follow the project `LICENSE`.*
