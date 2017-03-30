library(digest)

hash_list <- function(folder, hash_algorithm="sha256") {
  filelist = sort(list.files(folder, recursive = T))
  hashes = c()
  for (f in filelist) {
    hashes = c(hashes, 
               file_hash(filename=file.path(folder, f),
                         hash_algorithm=hash_algorithm))
  }  
  rtn = ""
  for (i in 1:length(hashes))
    rtn = paste0(rtn, hashes[i], "  ", filelist[i], sep="\n")
  class(rtn) = "hash_list"
  return(rtn)
}

write_hash_list <- function(hash_list, filename) {
  fl <- file(filename)
  writeLines(hash_list, fl, sep="")
  close(fl)
}

load_hash_list <- function(filename) {
  rtn = readChar(filename, file.info(filename)$size)
  class(rtn) = "hash_list"
  return(rtn)
}

file_hash <- function(filename, hash_algorithm="sha256") {
  x = readBin(filename, what="raw", n=file.info(filename)$size)
  return(digest(x, algo=hash_algorithm,  serialize = F))
}

print.hash_list <- function(x) {
  cat(x)
}
