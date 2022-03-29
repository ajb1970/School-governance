# Ofsted ratings of mainstream schools by governance

The Government often state that they intend to improve schools by encouraging or compelling maintained schools to convert to academy status. The evidence for this claim is not that extensive; however, the Department for Education did one study in 2014, [“Performance of converter academies: an analysis of inspection outcomes 2012 to 2013”](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/269332/DFE-RR322_-_Converter_Academies_Ofsted.pdf) . We have examined the performance of schools and academies by their governance type to see how this picture has developed over the last decade.

We have taken Ofsted’s release of [Ofsted outcomes](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1059521/Management_information_-_state-funded_schools_-_as_at_28_Feb_2022.xlsx) and looked at the outcomes for the last two full inspections (Section 5). We broke schools down into groups by phase: maintained local authority (maintained) schools that have been inspected twice; maintained schools that were previously inspected by Ofsted and then re-inspected having converted to a single-academy trust (SAT); maintained schools that were previously inspected by Ofsted and then re-inspected having converted to a multi-academy trust (MAT); schools that were inspected twice as a SAT; and finally, schools that were inspected twice as part of the same MAT. 

[edubase.py](edubase.py) downloads the latest version of school information from [Get Information About Schools](https://get-information-schools.service.gov.uk/Downloads).

[governance_ofsted_comparison.py](governance_ofsted_comparison.py) collates the Ofsted outcomes for schools by school governance type (local authority maintained, single-academy trust, multi-academy trust etc.) and saves Excel files to the [output folder](output).

The final report is [What is the evidence for forcing schools into multi-academy trusts.pdf](What%20is%20the%20evidence%20for%20forcing%20schools%20into%20multi-academy%20trusts.pdf).
