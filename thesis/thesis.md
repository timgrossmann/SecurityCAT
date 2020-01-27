# Automated Security and Policy testing for cloud applications using a Requirement Automation Tool

## Acknowledgements

## Abstract

## List of Figures


## Introduction´
Why testing at all?
What happens when testing?
Model based approach, how to know what is wrong or right without a defined model?
Where is the model in Azure etc.
Abstract testing further with a middle layer that triggers testing for different platforms?
Lacks systematic approach

**Model based approach**: Replaces test design by automated test generation based on model of architecture or system
**Test automation approach**: Replaces manual execution of designed test cases by automated test scripts
We use test automation approach

### Traditional testing

#### Source Code leak testing
Checking for leaked credentials etc.

#### Governance & Compliance
What is governance and compliance?

#### Functional security testing
Check functionality, efficiency, and availabilty

#### Security Vulnerable testing (Penetration testing)
Testing infrastructure and applications on infrastructure for vulnerabilites

### On the need for automated testing
No right or wrong without a model?

#### Resource testing with Policies
Example approach of Azure template model architecture for testing of policies.

#### DevSecOps
Security testing as part of the integration and deployment cycle.

#### Drawbacks of automated testing
Decision on compliance? 

### Related Work 
https://arxiv.org/pdf/1202.6118.pdf
https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4159681


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


#### OWASP
What is OWASP what is part of it?

#### EISA 
What is EISE what is part of it?
What is the Bosch way of defining it?
http://www.intranet.bosch.com/doku/eisa/

### Proof of Concept implementation

#### Architecture

#### Microsoft Azure Policies & Amazon Web Services Config Rules

#### Automated Security testing with Pacu & ZAP, Metasploit autopwn?

#### Custom scripts... ?

## Summary & Conclusion

## References