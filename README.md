# N-body Problem

**Ciljna ocena:** 10

## 1. Opis Problema

Ovaj projekat se bavi rešavanjem **problema n-tela (n-body problem)**. Problem n-tela podrazumeva simulaciju dinamičkog sistema čestica (tela) koje interaguju jedna sa drugom pod uticajem fizičkih sila, najčešće gravitacije. Cilj simulacije je predvideti kretanje, odnosno putanje ovih tela kroz vreme na osnovu njihovih početnih pozicija, masa i brzina.

Svako telo u sistemu privlači svako drugo telo silom koja je definisana Njutnovim zakonom opšte gravitacije:
$$ F = G \frac{m_1 m_2}{r^2} $$
gde su $m_1$ i $m_2$ mase dva tela, $r$ je udaljenost između njih, a $G$ je gravitaciona konstanta.

Računarska kompleksnost izračunavanja sila u svakom vremenskom koraku je $O(n^2)$, jer je potrebno izračunati interakciju za svaki par tela. Ovo čini problem računski veoma intenzivnim i idealnim kandidatom za paralelizaciju.

Simulacija se izvršava kao iterativni proces u diskretnim vremenskim koracima ($\Delta t$). U svakom koraku, stanje sistema se ažurira primenom **Euler-ove metode integracije**:

1.  **Izračunavanje Sila:** Za svako telo $i$, izračunava se ukupna sila $\vec{F_i}$. Sila između dva tela definisana je Njutnovim zakonom, uz dodatak **softening faktora ($\epsilon$)** u imeniocu kako bi se izbegla numerička nestabilnost (deljenje nulom) kada su tela previše blizu:
    $$ \vec{F}_{ij} = G \frac{m_i m_j}{|\vec{r}_{ij}|^2 + \epsilon^2} \cdot \frac{\vec{r}_{ij}}{|\vec{r}_{ij}|} $$

2.  **Ažuriranje Brzine:** Na osnovu ukupne sile $\vec{F_i}$ i drugog Njutnovog zakona ($\vec{a_i} = \vec{F_i} / m_i$), izračunava se nova brzina:
    $$ \vec{v}_{i, novo} = \vec{v}_{i, staro} + \vec{a_i} \cdot \Delta t $$

3.  **Ažuriranje Pozicije:** Nova pozicija tela se određuje na osnovu njegove nove brzine:
    $$ \vec{p}_{i, novo} = \vec{p}_{i, staro} + \vec{v}_{i, novo} \cdot \Delta t $$

Ovaj ciklus se ponavlja za definisani broj koraka, a pozicije tela se zapisuju u izlaznu CSV datoteku za kasniju analizu i vizualizaciju.

## 2. Planirane Metode za Rešavanje

Projekat će biti realizovan u više faza, u skladu sa zahtevima za ciljnu ocenu 10.

* **Paralelizacija u Python-u:** Korišćenje `multiprocessing` biblioteke za paralelizaciju na više procesorskih jezgara. Glavni fokus će biti na paralelizaciji petlje za izračunavanje sila.
* **Paralelizacija u Rust-u:** Korišćenje niti (`threads`) za postizanje paralelizma.
* **Analiza performansi:** Biće sprovedeni eksperimenti **jakog i slabog skaliranja** za obe implementacije (Python i Rust) kako bi se izmerilo ubrzanje i efikasnost paralelnih rešenja.
* **Vizualizacija:** Kreiranje 2D vizualizacije simulacije u Rust okruženju (koristeći biblioteku kao što je `Plotters`) na osnovu podataka generisanih tokom simulacije.

## 3. Paralelizacija

Računski najintenzivniji deo algoritma je **izračunavanje sila**, sa složenošću **$O(N^2)$**, i on predstavlja glavno usko grlo.

### Paralelizacija u Python-u

**Strategija paralelizacije u Python-u** je implementirana na sledeći način:
* Koristi se `multiprocessing.Pool` za kreiranje grupe radničkih procesa, čiji se broj može kontrolisati preko `--cores` argumenta komandne linije.
* U svakom koraku simulacije, funkcija `functools.partial` se koristi za kreiranje privremene radničke funkcije (`worker_func`) koja zna trenutne pozicije i mase svih tela.
* Glavna funkcija `pool.map` zatim distribuira posao pozivom `worker_func` za svako telo u sistemu, raspoređujući izračunavanje sila na sva dostupna jezgra.
* Nakon što svi procesi završe, glavni proces prikuplja rezultate i nastavlja sa sekvencijalnim ažuriranjem brzina i pozicija.

### Paralelizacija u Rust-u

**Strategija paralelizacije u Rust-u** je implementirana na sledeći način:
* Koristi se biblioteka **Rayon** i njen "work-stealing" thread pool, čiji se broj niti može kontrolisati preko `--cores` argumenta komandne linije.
* U svakom koraku simulacije, pozivom metode `par_iter()` na vektoru tela, sekvencijalni iterator se transformiše u paralelni, pripremajući sistem za distribuciju posla.
* Rayon zatim distribuira posao tako što za svako telo paralelno izvršava `map()` operaciju (closure) koja računa ukupnu silu za to telo.
* Nakon što sve niti završe svoje izračunavanje, metoda `collect()` sakuplja rezultate u jedinstveni vektor sila, nakon čega se nastavlja sa sekvencijalnim ažuriranjem brzina i pozicija.

## 4. Planirani Eksperimenti i Analiza Performansi

Da bi se kvantifikovalo ubrzanje dobijeno paralelizacijom, biće sprovedena dva standardna tipa eksperimenata za obe implementacije (Python i Rust).

### Eksperiment Jakog Skaliranja (Strong Scaling)
* **Cilj:** Izmeriti ubrzanje pri rešavanju problema **fiksne veličine**.
* **Metodologija:** Broj tela u simulaciji će biti fiksiran (npr. $N=100$). Program će se pokretati sa progresivno većim brojem jezgara (1, 2, 4, 8, ...). Meriće se vreme izvršavanja za svaku konfiguraciju.
* **Analiza:** Izmereno ubrzanje ($Speedup = T_1 / T_P$, gde je $T_P$ vreme sa $P$ jezgara) biće upoređeno sa teorijskim ubrzanjem predviđenim **Amdalovim zakonom**.

### Eksperiment Slabog Skaliranja (Weak Scaling)
* **Cilj:** Izmeriti sposobnost sistema da rešava **sve veći problem** u istom vremenskom roku, uz dodavanje više procesora.
* **Metodologija:** Opterećenje po procesorskom jezgru će se održavati konstantnim. Pošto složenost problema raste sa $O(N^2)$, prilikom povećanja broja jezgara ($P$), broj tela ($N$) će se povećavati za faktor $\sqrt{P}$.
* **Analiza:** Efikasnost i ubrzanje će se uporediti sa teorijskim modelom definisanim **Gustafsonovim zakonom**.
