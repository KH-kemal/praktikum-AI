% fakta mahasiswa(nama, IPK, penghasilan_orang_tua, prestasi).
% rendah = 0 - 2.5jt/bulan
% sedang = 2.5jt - 5jt/bulan
% tinggi = > 5jt/bulan

mahasiswa(kemal, 3.5, sedang, ada).
mahasiswa(dika, 3.8, tinggi, ada).
mahasiswa(putri, 3.2, rendah, tidak).
mahasiswa(dedi, 2.9, rendah, tidak).

% Beasiswa Prestasi

rekomendasi(Nama, beasiswa_prestasi) :-
    mahasiswa(Nama, IPK, _, ada),
    IPK >= 3.5.

% Beasiswa Kurang Mampu
rekomendasi(Nama, beasiswa_kurang_mampu) :-
    mahasiswa(Nama, IPK, rendah, _),
    IPK >= 3.0.

% Beasiswa Umum
rekomendasi(Nama, beasiswa_umum) :-
    mahasiswa(Nama, IPK, _, _),
    IPK >= 3.0.

