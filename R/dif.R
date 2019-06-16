library(digest)

CHECKSUMS_SEPERATOR = "  "

file_hash <- function(filename, hash_algorithm="sha256") {
  x = readBin(filename, what="raw", n=file.info(filename)$size)
  return(digest(x, algo=hash_algorithm,  serialize = F))
}

DIF <- function(folder, hash_algorithm="sha256") {
  filelist = list.files(folder, recursive=T, all.files=T)
  hashes = c()
  for (f in filelist) {
    hashes = c(hashes, 
               file_hash(filename=file.path(folder, f),
                         hash_algorithm=hash_algorithm))
  }  
 
  rtn = list()
  rtn$folder = folder
  rtn$hash_algorithm = hash_algorithm
  rtn$hashes = hashes
  rtn$files = filelist
  class(rtn) = "DIF"
  return(sort(rtn))
}

sort.DIF <- function(x) {
  # sorting byte-wise (captial letters first) like unix under locale "C"
  idx = order(x$hashes, x$files, method="radix")
  x$hashes = x$hashes[idx]
  x$files = x$files[idx]
  return(x)
}


print.DIF <- function(x) {
  cat("Folder: ")
  cat(x$folder)
  cat(" (files n=")
  cat(length(x$hashes))
  cat(")")
  cat("\nAlgorithm: ")
  cat(x$hash_algorithm)
  cat("\nMaster hash: ")
  cat(master_hash(x), "\n")
}

summary.DIF <- function(x) {
  cat(checksums(x))
}

checksums <- function(x) {
  rtn = ""
  for (i in 1:length(x$hashes)) {
    l = paste0(x$hashes[i], CHECKSUMS_SEPERATOR, x$files[i], sep="\n")
    rtn = paste0(rtn, l)
  }
  return(rtn)
}

master_hash <- function(x) {
  return(digest(checksums(x), algo=x$hash_algorithm,  serialize = F))
}

write_checksums <- function(dif, filename) {
  fl <- file(filename)
  writeLines(checksums(dif), fl, sep="")
  close(fl)
}

load_checksums <- function(filename, hash_algorithm="sha256") {
  rtn = list()
  rtn$folder = NA
  rtn$hash_algorithm = hash_algorithm
  rtn$hashes = c()
  rtn$files = c()
  fl = file(filename, "r")
  while ( TRUE ) {
    line = readLines(fl, n = 1)
    if ( length(line) == 0 ) {
      break
    }
	line = unlist(strsplit(line, CHECKSUMS_SEPERATOR))
	rtn$hashes = c(rtn$hashes, line[1])
	rtn$files = c(rtn$files, line[2])
  }
  close(fl)
  class(rtn) = "DIF"
  return(sort(rtn))
}
