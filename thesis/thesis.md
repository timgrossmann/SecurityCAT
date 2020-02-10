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

**Model based approach**: Replaces test design by automated test generation based on model of architecture or system
Infrastructure as code, tools e.g. terraform, infrastructure defined through a config file (properties easily testable)

Compliance system in e.g. (Policies) Azure, (Config Rules) AWS 

**Test automation approach**: Replaces manual execution of designed test cases by automated test scripts
We use test automation approach

### Traditional testing

#### Source Code leak testing (static source code analysis)
Checking for leaked credentials etc. (https://www.gitguardian.com/private)
Security testing for source code (https://owasp.org/www-community/Source_Code_Analysis_Tools)
Strengths
    Scales well – can be run on lots of software, and can be run repeatedly (as with nightly builds or continuous integration)
    Useful for things that such tools can automatically find with high confidence, such as buffer overflows, SQL Injection Flaws, and so forth
    Output is good for developers – highlights the precise source files, line numbers, and even subsections of lines that are affected
Weaknesses
    Many types of security vulnerabilities are difficult to find automatically, such as authentication problems, access control issues, insecure use of cryptography, etc. The current state of the art only allows such tools to automatically find a relatively small percentage of application security flaws. However, tools of this type are getting better.
    High numbers of false positives.
    Frequently can’t find configuration issues, since they are not represented in the code.
    Difficult to ‘prove’ that an identified security issue is an actual vulnerability.
    Many of these tools have difficulty analyzing code that can’t be compiled. Analysts frequently can’t compile code because they don’t have the right libraries, all the compilation instructions, all the code, etc.


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


#### Resource testing with Policies
Example approach of Azure template model architecture for testing of policies.


#### DevSecOps
The concept behind DevSecOps integrates automated security testing into the continous quality assurance of continous development, integration, and deployment. 
It combines Development, Security, and Operations to improve the speed, turnover time, and overall quality of products.

Manual security, and compliance testing slows down release processes and therefore needs to be augmented with automated testing, and integrated into the continous software deployment lifecycle.

![DevSecOps life cylce](https://twitter.com/LMaccherone/status/843644744538427392/photo/1)

The schematic drawing of DevSecOps displays and explains the major elements of the life cylce.
Security is implemented in the overall process and breaches in security or compliance lead to interrupted releases.
In the operations phase, intrusions are detected, countermeasures taken, and attacks analysed which enables reporting that can be leveraged to improve the quality and secrity of the product in the development pase. 


#### Drawbacks of automated testing
Decision on compliance? 
Security is an extremely complex topic...


### Related Work 
https://arxiv.org/pdf/1202.6118.pdf
https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4159681
Cloud Security Automation Framework: https://ieeexplore.ieee.org/document/8064140



## An approach to automated testing using a Requirement Automation Tool (RAT) 
### Current approach to testing
How does Bosch currently test the applications?
Workflow etc.

### SecurityRAT
Where do requirements come from and which requirements are important?
How to decide what is important?

OWASP Security RAT (Requirement Automation Tool) is a tool supposed to assist with the problem of addressing security requirements during application development. The typical use case is:

- specify parameters of the software artifact you're developing
- based on this information, list of common security requirements is generated
- go through the list of the requirements and choose how you want to handle the requirements
- persist the state in a JIRA ticket (the state gets attached as a YAML file)
- create JIRA tickets for particular requirements in a batch mode in developer queues
- import the main JIRA ticket into the tool anytime in order to see progress of the particular tickets

... Example image of SecurityRAT


#### OWASP
What is OWASP what is part of it?

The Open Web Application Security Project, or OWASP, is an international non-profit organization dedicated to web application security. One of OWASP’s core principles is that all of their materials be freely available and easily accessible on their website, making it possible for anyone to improve their own web application security. The materials they offer include documentation, tools, videos, and forums. 

The OWASP Foundation, a 501(c)(3) non-profit organization (in the USA) established in 2004, supports the OWASP infrastructure and projects. Since 2011, OWASP is also registered as a non-profit organization in Belgium under the name of OWASP Europe VZW.

#### EISA 
What is EISE what is part of it?
What is the Bosch way of defining it?
http://www.intranet.bosch.com/doku/eisa/

 Bosch EISA defines the Bosch basic protection level and the building blocks of IT security by defining

    What IT security controls shall be put in place in order to be resilient against IT security threats,

    How these security controls are positioned,

    How they relate to each other and to the overall Enterprise IT architecture.

Bosch EISA aims to enable IT organizations, projects and associates across the entire Bosch Group (RBW) to

    gain a common understanding of IT Security,

    ensure the consistent implementation of a common security baseline,

    enhance compliance with Bosch-internal guidelines and regulations (primarily C/ISP CD 02900), and

    align Bosch IT security with industry and government standards, for example:

        ISO 27001 (full text in Bosch NormMaster),

        Cloud Security Alliance (CSA) Cloud Control Matrix (CCM)

        NIST Special Publication 800-53

According to RB/GF 00177 C/IDS has the Governance Function for IT Security at Bosch.

    “IT Security (Cyber Security) are technologies, processes and measures that protect IT systems and electronic information against internal and external cyber attacks (e.g. cyber espionage, extortion, sabotage).” (RB/GF 00177-002 - 2.19)

    “Best in Class IT Security is a key factor for both internal and external digital products and services, which has to be ensured over the complete life cycle.” (RB/GF 00177-4.1) 

C/IDS defines the Bosch IT Security Framework on a strategic level by providing IT Security guard rails for Bosch to protect Bosch Business Models, Products, Services and Data.


### Proof of Concept implementation

Gateway

Policy MS

ZAP

#### Architecture

#### Microsoft Azure Policies & Amazon Web Services Config Rules

#### Automated Security testing with Pacu & ZAP, Metasploit autopwn?

#### Custom scripts... ?

## Summary & Conclusion

## References