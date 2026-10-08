# The FAQ in id; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Apa itu prepza?",
        "answer": "Wawancara berbatas waktu yang dibuat dari deskripsi pekerjaanmu, untuk posisi apa pun. Gunakan untuk menyaring kandidat sebelum kamu bertemu mereka, atau sebagai salah satu tahap rekrutmen itu sendiri: dengan cara mana pun, kamu melihat siapa yang benar-benar menguasai pekerjaannya.",
    },
    {
        "key": "roles",
        "question": "Untuk posisi apa saja aku bisa merekrut?",
        "answer": "Posisi apa pun yang membutuhkan pengetahuan: customer support, sales, keuangan, kesehatan, teknisi lapangan, engineering, pemasaran, dan lainnya. Jika kamu bisa menjelaskan pekerjaannya, prepza bisa membuat wawancara untuknya.",
    },
    {
        "key": "hiring",
        "question": "Bagaimana cara kerjanya?",
        "answer": "Tempel deskripsi pekerjaan di beranda, beri nama perusahaanmu, dan periksa topik yang diusulkan prepza. Lalu undang kandidat: ketik email mereka, tempel daftar, atau unggah file. Kandidat yang belum mulai setelah beberapa hari mendapat satu pengingat. Setiap kandidat mendapat soalnya sendiri dengan batas waktu di tiap soal, dan kamu melihat skor serta setiap jawabannya begitu mereka selesai.",
    },
    {
        "key": "link",
        "question": "Bisakah aku memasang wawancara di iklan lowongan?",
        "answer": "Bisa. Aktifkan tautan wawancara yang bisa dibagikan di tab kandidatnya, lalu tempel di iklanmu. Siapa pun yang membukanya masuk dan mengikuti wawancara, dan setiap orang dikenai biaya seperti kandidat yang diundang. Tautan nonaktif saat kamu menandai wawancara dengan status Diterima.",
    },
    {
        "key": "preview",
        "question": "Bisakah aku mencoba wawancara sebelum mengundang siapa pun?",
        "answer": "Bisa. Buka wawancaramu sebagai kandidat dari halamannya, gratis: pratinjau tidak muncul di antara kandidatmu atau di statistik soal. Kamu juga bisa mengikuti wawancara latihan gratis mana pun.",
    },
    {
        "key": "cheating",
        "question": "Bisakah kandidat memakai AI atau mencari jawabannya?",
        "answer": "Setiap kandidat mendapat soal acak sendiri dengan urutan sendiri, dengan batas waktu di tiap soal yang dijaga server kami, jadi hanya ada sedikit waktu untuk mencari jawaban atau bertanya ke AI. Scorecard juga menunjukkan saat kandidat meninggalkan halaman, menyalin teks, atau menjawab terlalu cepat untuk sempat membaca soal.",
    },
    {
        "key": "cost",
        "question": "Berapa biayanya?",
        "answer": "Membuat wawancara gratis. Setiap kandidat yang menjawab setidaknya satu soal seharga {candidate} kredit (${candidate_dollars}), dan lebih murah dengan kredit dari isi ulang yang lebih besar, hingga $1. Perusahaan pertamamu mendapat {company} kredit gratis, cukup untuk {company_candidates} kandidat pertamanya. Halaman harga mencantumkan semua harga.",
    },
    {
        "key": "charged",
        "question": "Kapan kandidat dikenai biaya?",
        "answer": "Hanya saat mereka menyelesaikan wawancara setelah menjawab setidaknya satu soal. Kredit mereka disisihkan saat kamu mengundang mereka dan kembali jika kamu mencabut undangan, jika mereka tidak pernah mulai, atau jika mereka tidak menjawab apa pun.",
    },
    {
        "key": "compare_hiring",
        "question": "Bagaimana harganya dibanding alat asesmen lain?",
        "answer": "Banyak alat asesmen dijual sebagai langganan bulanan atau tahunan yang tetap dibayar meski kamu tidak menguji siapa pun. Di prepza kamu hanya membayar per kandidat: {candidate} kredit (${candidate_dollars}), tanpa kontrak, tanpa biaya per pengguna, dan tanpa biaya untuk membuat wawancara. Perusahaan yang mengundang {example_candidates} kandidat per bulan membayar sekitar ${example_year_dollars} per tahun. Jika kamu menguji banyak kandidat setiap bulan, langganan bisa lebih murah, jadi bandingkan dengan angkamu sendiri.",
    },
    {
        "key": "expire",
        "question": "Apakah kredit bisa kedaluwarsa?",
        "answer": "Tidak. Kredit tidak pernah kedaluwarsa, dan tidak ada langganan berbayar. Jika Anda menyalakan isi ulang otomatis yang opsional, Paddle menyimpan kartu Anda sebagai langganan $0; Anda hanya membayar isi ulang yang dilakukannya.",
    },
    {
        "key": "refunds",
        "question": "Bisakah aku mendapat pengembalian dana?",
        "answer": "Bisa, untuk kredit yang kamu beli dalam 14 hari terakhir dan belum dipakai: lewat Paddle atau dengan menulis kepada kami. Kredit gratis, seperti hadiah sambutan, tidak dikembalikan. Rinciannya ada di ketentuan.",
    },
    {
        "key": "scorecards",
        "question": "Apa yang ditampilkan scorecard?",
        "answer": "Setiap jawaban, apakah benar, dan berapa lama waktunya. Nilai tampil hijau atau merah dibanding nilai lulus yang kamu tetapkan untuk wawancara. Scorecard juga menandai jawaban yang terlalu cepat untuk sempat membaca soal, saat kandidat meninggalkan halaman, dan upaya menyalin.",
    },
    {
        "key": "reports",
        "question": "Bisakah aku membagikan hasil ke hiring manager?",
        "answer": "Bisa. Unduh laporan PDF untuk satu kandidat atau semua kandidat sebuah wawancara, kirim lewat email langsung dari prepza, atau kirim ringkasan singkat di WhatsApp, Telegram, Viber, atau LINE.",
    },
    {
        "key": "integrations",
        "question": "Apakah prepza bisa dipakai dengan ATS atau tools lain yang saya gunakan?",
        "answer": "Bisa, tanpa biaya tambahan. Hubungkan Workable, Greenhouse, Teamtailor, Recruitee, atau Breezy HR di tab Integrasi perusahaanmu: kandidat yang kamu pindahkan ke suatu tahap mendapat wawancara, dan hasilnya dikirim kembali ke ATS. Slack bisa memposting notifikasi perusahaanmu ke sebuah channel, dan API memungkinkan platformmu sendiri mengundang kandidat serta menerima hasil mereka; lihat Dokumentasi API.",
    },
    {
        "key": "candidates",
        "question": "Apa yang dilihat kandidat?",
        "answer": "Nama dan logo perusahaanmu, apa yang bisa diharapkan sebelum mulai, lalu satu soal berbatas waktu setiap kalinya. Mereka tidak pernah melihat skornya atau apakah jawabannya benar.",
    },
    {
        "key": "verified",
        "question": "Apa arti tanda centang terverifikasi?",
        "answer": "Artinya pemilik atau admin perusahaan masuk dengan email kerja di domain situs perusahaan, misalnya you@acme.com, lalu tim kami meninjau perusahaan tersebut. Tambahkan situsnya lewat Verifikasi di header perusahaanmu; layanan email gratis tidak dihitung. Selama masih menunggu peninjauan, timmu melihat ikon jam di samping nama, dan mengganti nama perusahaan mengirimnya untuk ditinjau lagi. Tanda centang tampil di samping nama perusahaanmu, termasuk di undangan.",
    },
    {
        "key": "languages",
        "question": "Bahasa apa saja yang didukung?",
        "answer": "{count} bahasa, untuk situs, wawancara, dan email. Pilih bahasa penulisan wawancara, apa pun bahasa deskripsi pekerjaannya.",
    },
    {
        "key": "privacy",
        "question": "Apa yang terjadi pada deskripsi pekerjaan dan jawaban?",
        "answer": "Deskripsi pekerjaan dipakai untuk membuat wawancaramu, dan jawaban kandidat untuk menilainya, hanya untuk perusahaanmu. Kebijakan privasi menjelaskan apa yang kami simpan, berapa lama, dan hak setiap orang.",
    },
    {
        "key": "emails",
        "question": "Email apa saja yang dikirim prepza, dan bagaimana cara menghentikannya?",
        "answer": 'Email layanan, seperti undangan, laporan, masalah pembayaran, dan perubahan ketentuan kami, selalu dikirim. Sisanya, seperti ringkasan aktivitas harian, pengingat, dan pembaruan produk, kamu pilih di Pengaturan, bagian Email, atau hentikan dengan tautan "Berhenti berlangganan" di setiap email. Kandidat bisa menghentikan email dari perusahaanmu, atau pengingat sebuah wawancara, lewat tautan di undangan dan pengingat mereka.',
    },
    {
        "key": "delete",
        "question": "Bisakah aku menghapus akunku?",
        "answer": "Bisa, di Pengaturan. Akun dan datamu dihapus, dan sebelumnya kamu bisa mengunduh salinan datamu.",
    },
]
