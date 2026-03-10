% fakta

lulusan_sd(anas).
wni(anas).
lahir(anas, 1952).
daftar_pns(anas, 1985).
tahun_sekarang(2005).

% aturan
% menghitung umur
umur(X, U) :-
    lahir(X, Tlahir),
    tahun_sekarang(Tsekarang),
    U is Tsekarang - Tlahir.

% Syarat tidak bisa menjadi PNS
tidak_bisa_jadi_pns(X) :-
    wni(X),
    lulusan(X, sd),
    umur(X, U),
    U > 35.

% PNS akan pensiun jika umur mencapai 60
pensiun(X) :-
    umur(X, U),
    U >= 60.