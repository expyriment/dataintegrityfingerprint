library(digest)

sha1_file <- function(filename) {
  x = readBin(filename, what="raw", n=file.info(filename)$size)
  return(digest(x, algo="sha1",  serialize = F))
}

checksum_list <- function(folder) {
  filelist = sort(list.files(folder, recursive = T))
  hashes = c()
  for (f in filelist) {
    hashes = c(hashes, 
             sha1_file(file.path(folder, f)))
  }  
  
  cs_str = checksum_list.as.string(list(hash=hashes, file=filelist))
  
  digest(cs_str, algo="sha1",  serialize = F)
  
  rtn = list(hash = hashes, file=filelist,
             master_hash = master_hash(hashes))
  class(rtn) = "checksum_list"
  return(rtn)
}

checksum_list.as.string <- function(x) {
  rtn = ""
  for (i in 1:length(x$hash))
    rtn = paste0(rtn, x$hash[i], "  ", x$file[i], sep="\n")
  return(rtn)
}

print.checksum_list <- function(x) {
  cat(checksum_list2string(x))
}

summary.checksum_list <- function(x) {
  cat(length(x$file), "files\nmaster hash:", data_finger_print(x))
}

write_checksum_list <- function(chksum_list, filename) {
  fl <- file(filename)
  writeLines(checksum_list2string(chksum_list), 
             fl, sep="")
  close(fl)
}



data_fingerprint <- function(folder) {
  cs = checksum_list(folder)
  return(master_hash(cs))
}
  