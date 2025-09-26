# N-body Problem

**Ciljna ocena:** 10

## 1. Opis Problema

Ovaj projekat se bavi rešavanjem **problema n-tela (n-body problem)**. Problem n-tela podrazumeva simulaciju dinamičkog sistema čestica (tela) koje interaguju jedna sa drugom pod uticajem fizičkih sila, najčešće gravitacije. Cilj simulacije je predvideti kretanje, odnosno putanje ovih tela kroz vreme na osnovu njihovih početnih pozicija, masa i brzina.

Svako telo u sistemu privlači svako drugo telo silom koja je definisana Njutnovim zakonom opšte gravitacije:
$$ F = G \frac{m_1 m_2}{r^2} $$
gde su $m_1$ i $m_2$ mase dva tela, $r$ je udaljenost između njih, a $G$ je gravitaciona konstanta.

Računarska kompleksnost izračunavanja sila u svakom vremenskom koraku je $O(n^2)$, jer je potrebno izračunati interakciju za svaki par tela. Ovo čini problem računski veoma intenzivnim i idealnim kandidatom za paralelizaciju.

## 2. Planirane Metode za Rešavanje

Projekat će biti realizovan u više faza, u skladu sa zahtevima za ciljnu ocenu 10.

* **Paralelizacija u Python-u:** Korišćenje `multiprocessing` biblioteke za paralelizaciju na više procesorskih jezgara. Glavni fokus će biti na paralelizaciji petlje za izračunavanje sila.
* **Paralelizacija u Rust-u:** Korišćenje niti (`threads`) za postizanje paralelizma.
* **Analiza performansi:** Biće sprovedeni eksperimenti **jakog i slabog skaliranja** za obe implementacije (Python i Rust) kako bi se izmerilo ubrzanje i efikasnost paralelnih rešenja.
* **Vizualizacija:** Kreiranje 2D vizualizacije simulacije u Rust okruženju (koristeći biblioteku kao što je `Plotters`) na osnovu podataka generisanih tokom simulacije.
