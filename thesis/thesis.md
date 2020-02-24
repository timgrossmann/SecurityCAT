# Automated Security and Policy testing for cloud applications using a Requirement Automation Tool

## Acknowledgements

## Abstract

## List of Figures


## Introduction
Why testing at all?

Especially in the corporate world, projects pass so called Quality Gates which also require a baseline of compliance and security testing to be done.
(Quality Gates at Bosch) 

What happens when testing?
Model based approach, how to know what is wrong or right without a defined model?
Where is the model in Azure etc.
Abstract testing further with a middle layer that triggers testing for different platforms?
Lacks systematic approach

Requirement automation tool?


*Model based approach*: Replaces test design by automated test generation based on model of architecture or system
Infrastructure as code, tools e.g. terraform, infrastructure defined through a config file (properties easily testable)

Azure: https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/template-syntax

Compliance system in e.g. (Policies) Azure, (Config Rules) AWS 

Why we need a model?

*Planning based approach*: 
Testing based on plannning:
https://hal.inria.fr/hal-01405274/document


*Test automation approach*: Replaces manual execution of designed test cases by automated test scripts
We use test automation approach


### Traditional testing

#### Static source code analysis (Static Application Security Testing (SAST))
The "Static Source Code Analysis", as the name suggests, is performed without executing the program. It is a crucial approach to review the formal correctness, data-flow, and even credential leaks.
Static code analysis normally implemented as one of the first gates of continous integration pipelines.

Depending on the focus of the analysis, there are different state-of-the-art providers for static code analysis like for example credential checking on Open-Source platforms like GitHub using GitGuardian (https://www.gitguardian.com) 

When focusing on security testing with static analysis, problems that can be identified with high confidence have to be targeted. Those include for example SQL Injections and Buffer Overflows.
The OWASP-project provides a list of tooling that can (https://owasp.org/www-community/Source_Code_Analysis_Tools) be used as part of a continous integration pipeline. 
Once a vulnerability is found, the build fails and provides detailed reporting to the developers which have to fix the issues before future builds succeed.

However this approach has many drawbacks. It has a high rate of false positives which can greatly increase the time needed for manual testing and reviewing.
In addition to that, most security vulnerabilities are difficult to find automatically. Access control issues, insecure use of cryptography are only a few examples. Even misconfigurations can't be identified without a model based approach, as discussed before.


#### Governance & Compliance
What is governance and compliance?

https://dzone.com/articles/importance-governance-software
https://www.researchgate.net/publication/232643565_Software_Development_Governance_A_Meta-management_Perspective

https://www.red-gate.com/simple-talk/opinion/opinion-pieces/it-compliance-and-software-development/


#### Functional security testing
Check functionality, efficiency, and availabilty
Security testing for source code (https://owasp.org/www-community/Source_Code_Analysis_Tools)


#### Security Vulnerable testing (Penetration testing)
Testing infrastructure and applications on infrastructure for vulnerabilites
https://www.greycampus.com/blog/information-security/penetration-testing-step-by-step-guide-stages-methods-and-application


### On the need for automated testing
No right or wrong without a model?
Re-runnable (re-producable), comparably quick as part of the release process
Automated reports

"Intelligence" centralized in e.g. a DB with the attacks

https://www.breachlock.com/automated-penetration-testing-a-myth-or-reality/
https://blog.cymulate.com/automated-penetration-testing
https://www.securit360.com/blog/vulnerability-scan-not-penetration-test-pentest/
https://portswigger.net/testers/automated-penetration-testing
https://www.veracode.com/security/automated-penetration-testing-tools


> Automated pentration testing (San Jose)
> Yaroslav Stefinko, Manual and Automated Penetration Testing


#### Resource testing with Policies
Example approach of Azure template model architecture for testing of policies.


#### DevSecOps
The concept behind DevSecOps integrates automated security testing into the continous quality assurance of continous development, integration, and deployment. 
It combines Development, Security, and Operations to improve the speed, turnover time, and overall quality of products.

Manual security, and compliance testing slows down release processes and therefore needs to be augmented with automated testing, and integrated into the continous software deployment lifecycle.

![DevSecOps life cylce](./assets/devsecops.png)

The schematic drawing of DevSecOps displays and explains the major elements of the life cylce.
Security is implemented in the overall process and breaches in security or compliance lead to interrupted releases.
In the operations phase, intrusions are detected, countermeasures taken, and attacks analysed which enables reporting that can be leveraged to improve the quality and secrity of the product in the development pase. 


#### Drawbacks of automated testing
Security is an extremely complex topic...

Do not perform pivot attacks (compromising one machine and then launching attacks from that machine to other areas of the network)
Often times do not verify exploits (eliminate false positives)

They often result in false positives, false negatives, require frequent patching, and cannot properly test physical security

It might give a false sense of security. Being able to withstand most penetration testing attacks might give the sense that systems are 100% safe. In most cases, however, penetration testing is known to company security teams who are ready to look for signs and are prepared to defend. Real attacks are unannounced and, above all, unexpected.

> Yaroslav Stefinko, Manual and Automated Penetration Testing


### Related Work 
https://arxiv.org/pdf/1202.6118.pdf
https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4159681
Cloud Security Automation Framework: https://ieeexplore.ieee.org/document/8064140



## An approach to automated testing using a Requirement Automation Tool (RAT) 
### Current approach to testing
How does Bosch currently test the applications?
Workflow etc.



For external clients, the information from SecurityRAT is exported into an Excel file and filled in there.


### OWASP SecurityRAT
The OWASP Security Requirement Automation Tool, short SecurityRAT, is an application designed to streamline the management of security requirements throughout the development process.
It comes with an initial set of requirements stated in the ASVS (Application Security Verification Standard). Users, however, are encouraged to create their own set of requirements since risk profiles differ greatly between companies.
SecurityRAT emphasizes automation over merely listing requirements. Properties of an appication in development are secified, then used to filter down the set of requirements to only get the ones that have to be fulfilled. 

The set of requirements for example contains elements specific to Microsoft Azure Implementation. Each "Implementation Type" has it's own given set of requirements.

```math
MSA-... \strict\subset EISA
```

Where MSA is the set of requirements used in the evaluation of Microsoft Azure implementations. 

...add filter subset mathematical function, whole dataset subset when used azure etc.

The requirements can be annotaded about whether they have to be implemented or not. In addition to that, the reasoning or result can be documented in SecurityRAT.

![SecurityRAT screen](assets/secrat_screen.png)

The focus on automation becomes present through the integration of JIRA into the tool. JIRA tickets can automatically be created, tracked, and documented with SecurityRAT.

![SecurityRAT schema](assets/security_rat.png)
> Source: https://securityrat.github.io/

The process flow of SecurityRAT can be described as follows:
1. Property specification of the software project, called artifact 
1. Common security requirements are listed as a subset of the given requirements database
1. Decide which requirements are needed and how they are handled
1. Create automated JIRA tickets for state tracking of open issues

SecurityRAT provides additional automation for project ecxel sheet export, training slides creation, and with SecurityCAT, automted testing of trivial technical measures.



#### OWASP
The Open Web Application Security Project, short OWASP, is a non-profit organization which aims to improve web application security by providing freely available eductional material. The material includes different tooling, on-demand videos, forums and extensive documentation. 
The OWASP project is mostly known through the open-source projects, created and maintained by the community.
One of their most popular projects is the OWASP Top 10 which lists the most common vulnerabilities for web applications.


#### EISA 
EISA, short for Entreprise IT Security Architecure, is the internal IT Security Governance Framework used at Bosch.
International industry and government standards like the ISO27001, Cloud Security Aliance, and NIST Special Publication have been combined to enable Bosch businesses with a holistic view on IT Security.

It defines the building blocks and protection levels of IT security inside Bosch. Server operating systems, web servers, and networks are the resources in focus.   
The security controls provide a baseline to build infrastructure and project that are resilient against security threats.

The controls introduced through Bosch EISA aim to give a common understanding of IT security to associates across the entire Bosch Group as well as ensuring a consistent implementation of a security baseline that ensures compliance with internal guidelines and regulations.

### Proof of Concept implementation

SecurityCAT...

Gateway

Policy MS

ZAP

#### Architecture

#### Microsoft Azure Policies & Amazon Web Services Config Rules

Estimated Evaluation time and trigger time chart


#### Automated Security testing with Pacu & ZAP, Metasploit autopwn?



#### Custom scripts... ?

#### Semmle QL

## Summary & Conclusion

https://www.popularmechanics.com/technology/security/a16827/ai-capture-the-flag/
https://thenextweb.com/insider/2016/08/04/watch-ai-hack-darpa-cyber/
http://www.xinhuanet.com/english/2018-08/13/c_137387613.htm

## References