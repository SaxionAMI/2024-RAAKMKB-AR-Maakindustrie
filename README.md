# 2024-RAAKMKB-AR-Maakindustrie

Windows
=======

Installatie 
-----------


* Download en installeer python versie 3.10.0
	Ga naar: https://www.python.org/downloads/release/python-3100/
	Download de Windows installer (64-bit)
	Voer het gedownloade bestand uit om python te installeren. Selecteer de bovenste optie (standaard installatie)
* Maak een map aan op je systeem en kopieer de volgende bestanden naar die map:
	* process_video.py
	* video2instruction_UI.py
	* requirements.txt
* Open de map in de verkenner. Klik met de rechtermuisknop ergens in de map (in de 'lege ruimte', dus niet op een van de bestanden) en selecteer: "Open Terminal"
* voer het volgende commando in (en sluit dit af met enter):
	py -m pip install -r requirements.txt

  Python zal nu aanvullende benodigde bibliotheken installeren. Dit kan enige tijd in beslag nemen. Mogelijk verschijnen er diverse waarschuwingen; dat is geen probleem.

* Als de installatie klaar is (dat kan je oa zien doordat de opdrachtprompt '>' weer in beeld verschijnt in de terminal) kan de terminal worden gesloten.

Gebruik
-------
* Dubbelklik het bestand 'video2instruction.py' om het programma te starten.
* Bij de eerste keer gebruik zal er eerst een AI model worden gedownload dat gebruikt wordt voor de tekstanalyse. Dat kan enige tijd in beslag nemen.
* De eerste keer dat een filmpje wordt geanalyseerd zal er een transcriptiebestand worden gemaakt en opgeslagen in de aangegeven doelmap (ouput path). Dat kan de nodige tijd in beslag nemen (in een ander terminal venster zal een progress bar zichtbaar worden). Mocht je een paar kleine wijzigingen aan willen brengen in het rapport (bijvoorbeeld ander stopwoord of een andere titel), dan zal de tweede keer veel sneller zijn. Er wordt dan gebruik gemaakt van de bestaande transcriptie.
* Naast de transcriptie worden er een .md en een .html pagina aangemaakt waarin het rapport staat. Dit kan als basis dienen voor het uit te voeren stappenplan. In de meeste gevallen zal dit nog moeten worden aangescherpt. Het wijzigen van het stappenplan kan door rechtstreeks de html te wijzigen, of door de pagina te openen in Word bijvoorbeeld.



OSX / Linux
===========
Developed and tested using python 3.10. 

To use, first install all dependencies:

	pip install -r requirements.txt

Run the program with a simple user interface using

	python video2instruction_UI.py

UI settings are saved in the user's root folder in the file video2instruction_settings.cfg

To run without user interface, change the `main()` function in `process_video.py` and run

	python process_video.py

