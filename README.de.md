[![de](https://img.shields.io/badge/lang-de-green.svg)](README.de.md)
![GitHub License](https://img.shields.io/github/license/s-quirin/EasyGUIng)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/s-quirin/EasyGUIng)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/s-quirin/EasyGUIng)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/s-quirin/EasyGUIng/pyside6-essentials)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/s-quirin/EasyGUIng/matplotlib)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/s-quirin/EasyGUIng/pint)

# EasyGUIng
## Ein Framework zur Bereitstellung mathematischer Modelle mit Benutzeroberfläche
>Modell und GUI sind einfach zu erstellen für den Fachexperten und einfach zu nutzen für den Endanwender.

<img src="doc/Screenshot_model.png" alt="Code Ausschnitt" title ="Code des Modells" width="500"/>
<img src="doc/Screenshot.png" alt="Benutzeroberfläche" title ="GUI des Modells" width="500"/>

## Ziele
- [x] Kann vom Fachexperten mit **geringen Programmierkenntnissen** gefüttert werden
  - Die notwendige Programmierung ist auf den mathematischen Algorithmus beschränkt.
- [x] Kann an **jeden beliebigen** Nutzer verteilt und von diesem bedient werden
  - Die Verteilung ist unkompliziert und wird nicht durch Lizenzen limitiert.
- [x] Beliebige Komplexität der mathematischen Modelle und vollständige Freiheit in der Umsetzung
  - analytisch, numerisch, ML etc.

## Installation
Eine *Installation* ist nicht notwendig. Laden Sie sich eine [Release-Version](https://github.com/s-quirin/EasyGUIng/releases) herunter, entpacken sie und starten die enthaltene `EasyGUIng.exe`. Erstellen Sie mit [dieser Anleitung](#modellerstellung) direkt Ihr eigenes Modell.

Finden Sie keine für Ihr System passende Version, probieren Sie die Ausführungen zur [manuellen Installation](#manuelle-installation-in-python) in Python.

Unterstützung bei der Installation und bei der Implementierung Ihres Modells erhalten Sie gegen Entgelt beim [Lehrstuhl für Leichtbausysteme der Universität des Saarlandes](https://www.uni-saarland.de/lehrstuhl/herrmann). Gerne bieten [wir](https://www.uni-saarland.de/lehrstuhl/herrmann/team) Ihnen auch eine Kooperation in einem Forschungsprojekt an.

## Modellerstellung
- Erfolgt im Ordner `\model` als Textdatei mit Python-Code in der Form `Kurztitel.py`
- Der Inhalt kann aus den [frei verfügbaren](/model), kommentierten Beispielen kopiert werden.
- Erklärende Grafiken können als Vektorgrafiken (`Kurztitel.svg`) oder als Bilddateien (`.png`, etc.) abgelegt werden.

### Wie kann ich die Beispielmodelle anpassen?
1) Entfernen Sie den Lizenztext ab Zeile 4 oder ersetzen Sie ihn durch Ihren eigenen, wenn Sie Ihr Modell nicht frei der Allgemeinheit zur Verfügung stellen möchten.
1) Belassen Sie die sonstigen Kommentare (`#…`) und ändern Sie nicht die mit `# init` kommentierten Zeilen.
1) Füllen Sie zur Modellbeschreibung Titel, Beschreibung, Autor/Kontakt und Version mit Ihren anzuzeigenden Daten.
    >Tipp: Für `description` können Sie die Auszeichnungssprache [Markdown](https://de.wikipedia.org/wiki/Markdown) verwenden.
1) Füllen Sie die Informationen für Eingabewerte `input[…]` nach dem angegebenen Schema.
    ```
    input['x'] = ('Name', (minimaler Wert, …, maximaler Wert), 'Einheit')
    ```

    Verwenden Sie für `x` einen für dieses Modell eindeutigen Formelbuchstaben. Als Wert muss mindestens *ein* Zahlenwert angegeben werden. Weitere Werte sind optional und dienen zur Darstellung entsprechender Graphen.
1) `output` bezeichnet einen oder mehrere mögliche Ausgabewerte.
1) `plotX` legt die standardmäßig beim Start zu nutzende Laufvariable `'x'` fest.
1) Die Berechnungsvorschrift für das Modell findet sich in der Funktion `calculate` unter Nutzung von [NumPy](https://numpy.org/doc/stable/). Sie können zuvor definierte Konstanten `c`, Variablen `input['x']` als `var['x']` und die Namen von Ausgabewerten `output` als `out` verwenden.

## Manuelle Installation in Python
>Hier erfahren Sie, wie Sie das Programm lokal in einer Python-Umgebung ausführen.

Sie benötigen eine Installation von Python 3.10 auf Ihrem System, z. B. aus dem [Microsoft Store](https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5). Öffnen Sie in einer Python Konsole das Verzeichnis, in das Sie die [Projektdateien](/) heruntergeladen haben. Führen Sie nacheinander die folgenden Befehle aus.  
1. Prüfen Sie, ob `pip` installiert ist und installieren Sie `pipenv`:  
    ```shell
    python -m pip --version
    pip install pipenv
    ```
2. Generieren und starten Sie eine virtuelle Umgebung mit allen erforderlichen Abhängigkeiten:  
    ```shell
    pipenv --python 3.10
    pipenv install
    pipenv shell
    ```
3. Von hier aus können Sie das Programm direkt starten:
    ```shell
    python EasyGUIng.py
    ```
4. Möchten Sie ein gebündeltes Paket zum Verteilen (vgl. [Releases](https://github.com/s-quirin/EasyGUIng/releases)), erhalten Sie Support beim [Lehrstuhl für Leichtbausysteme der Universität des Saarlandes](https://www.uni-saarland.de/lehrstuhl/herrmann).

## Credits:
* 2022 – heute: [Steven Quirin](https://github.com/s-quirin), Universität des Saarlandes
