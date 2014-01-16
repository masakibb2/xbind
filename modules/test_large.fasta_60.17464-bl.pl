#!/usr/bin/perl
$host = shift;
$arg = shift;

#### random sleep, rand() can be a fraction of second
select(undef,undef,undef,rand());

if ($arg) {
  @ids = split(/,/, $arg);
}
else {
  while(1) {
    if (opendir(DDIR, "test_large.fasta_60-seq")) { 
      @ids = grep {/^\d+$/} readdir(DDIR);
      last;
    }
    else {
      sleep(1);
    }
  }
}

foreach $id (@ids) {

  next unless (-e "test_large.fasta_60-seq/$id");
  next if (-e "test_large.fasta_60-seq/$id.lock");
  $cmd = `touch test_large.fasta_60-seq/$id.lock`;

  if (0) {
    $cmd = `blastpgp -m 8 -d  -j 3 -F F -e 0.001 -b 500 -v 500 -i test_large.fasta_60-seq/$id -C test_large.fasta_60-bl/$id.prof`;
  }

  if (1) {
    $cmd = `blastall -p blastp -m 8 -d ./test_large.fasta_60.17464 -F F -e 0.000001 -b 100000 -v 100000 -i test_large.fasta_60-seq/$id | /usr/bin/psi-cd-hit.pl -J parse_blout test_large.fasta_60-bl/$id -c 0.3 -ce 1e-6 -aS 0.5 -aL 0.5 -G 1 -prog blastp -bs 1`;
  }
  else {
    $cmd = `blastall -p blastp -m 8 -d ./test_large.fasta_60.17464 -F F -e 0.000001 -b 100000 -v 100000 -i test_large.fasta_60-seq/$id -o test_large.fasta_60-bl/$id`;
    $cmd =                         `/usr/bin/psi-cd-hit.pl -J parse_blout test_large.fasta_60-bl/$id -c 0.3 -ce 1e-6 -aS 0.5 -aL 0.5 -G 1 -prog blastp -bs 0`;
  }
  $cmd = `rm -f  test_large.fasta_60-seq/$id`;
  $cmd = `rm -f  test_large.fasta_60-seq/$id.lock`;
  if (0) { $cmd = `rm -f  test_large.fasta_60-bl/$id.prof`; }
}

($tu, $ts, $cu, $cs) = times();
$tt = $tu + $ts + $cu + $cs;
$cmd = `echo $tt >> test_large.fasta_60-seq/host.$host.cpu`;

