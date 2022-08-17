# adaptiveVnonadaptive

## Scripts
In deze github staat de door mij geschreven code.
Als alle dependencies geïnstalleerd zijn vanuit requirements.txt zou een draaibare versie van de pipeline te vinden zijn in modified_pipeline.py
In deze python script wordt het hele experiment gedraaid exclusief de phospheensimulator (SPV) en DVS omdat deze van het donders instituut zijn.

In Analyse.py is de code te zien die ik heb gebruikt voor het inladen en inlezen van de verkregen testdata. Deze maakt gebruik van de combined_{test_mode}.json bestanden te vinden in /results/subjectdata/{test_modus}.

In Demo.py is een korte demonstratie te zien die ik gebruikt heb voor het inlichten van de proefpersonen.

In Objects.py staat een Subject object, gebruikt om gemakkelijk data uit te verkrijgen.

In prompt.py staan alle GUI's die gebruikt zijn

In original_experiment_pipeline.py staat de originele code, deze draait dus niet door het gebrek aan SPV en DVS.

##Controls

In modified_pipeline.py zijn de controls als volgt:
Als de variabele MODE op adaptive staat kan je met de muis de threshold (links en rechts ) en sigma (boven + beneden) aanpassen. Tijdens de video's kan je altijd de spatiebalk gebruiken om de video vroegtijdig te beïndigen. 

In demo.py zijn de controls als volgt:
Gebruik de pijltjes toetsen naar boven en naar beneden om verschillende schermen te laten zien, druk op esc om het af te sluiten. 
