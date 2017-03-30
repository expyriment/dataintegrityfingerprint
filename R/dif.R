source("hash_list.R")

dif <- function(folder, hash_algorithm="sha256") {
  return(hash_list2dif(hash_list(folder, hash_algorithm=hash_algorithm)))
}

hash_list2dif <- function(hash_list, hash_algorithm="sha256") {
  rtn = list()
  rtn$hash_list = hash_list
  rtn$hash_algorithm = hash_algorithm
  
  hashes = c()
  for (hash in unlist(strsplit(hash_list, "\n"))) {
    hashes = c(hashes, unlist(strsplit(hash, " "))[1])
  }
  rtn$n_files = length(hashes)       
  
  txt = ""
  for (hash in sort(hashes)) 
    txt = paste0(txt, hash)

  rtn$master_hash = digest(txt, algo=hash_algorithm,  serialize = F)
  class(rtn) = "dif"
  return(rtn)
}

print.dif <-function(x)  {
  cat(x$n_files, "files\nmaster hash:", x$master_hash)
}

summary.dif <- function(x) {df
  print(x$hash_list)
  cat("\n")
  print(x)
}
