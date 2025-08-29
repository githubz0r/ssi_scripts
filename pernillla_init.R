library(tidyverse)
library(magrittr)
library(pheatmap)
library(argparse)
library(readxl)
base_path <- '/Volumes/data/MPV/projects/SAB_Orebro/study3/data/'
base_path <- '~/ssi_stuff/for_michele/'
persistent_bacteremia <- read_tsv(paste0(base_path,'df.Rtab'))
view(persistent_bacteremia)

#treewas_pangenome <- read_excel(paste0(base_path, 'Set_persistent_bacteremia/treeWAS/fasttree_gubbins/pangenome_mapping_treewas.xlsx'))
gene_treewas <- read_excel(paste0(base_path, 'gene_treewas.xlsx'))
#treewas_rdata <- load(paste0(base_path, 'Set_persistent_bacteremia/treeWAS/fasttree_gubbins/gene_KMA_mapping_treeWAS.RData'))
gene_matrix <- read_tsv(paste0(base_path,'gene_presence_absence.Rtab'))
significant_genes <- gene_treewas %>% filter(terminal_pvalue<=0.05/nrow(gene_treewas) | simultaneous_pvalue<=0.05/nrow(gene_treewas) | subsequent_pvalue<=0.05/nrow(gene_treewas))
cor(persistent_bacteremia$Persistant_bacteremia, persistent_bacteremia$Comorbidity_uCCI)
gene_matrix %<>% rename('SSAB19166' = 'SSAB19166_1')
significant_sample_matrix <- gene_matrix %>% select(c('Gene', all_of(persistent_bacteremia$original_sample_name))) %>% filter(Gene %in% significant_genes$ID)
significant_sample_df <- significant_sample_matrix %>% data.frame(row.names = 'Gene') %>% t() %>% as.data.frame %>% rownames_to_column('sample_name')
joined_df <- persistent_bacteremia %>% select(original_sample_name, Sex_binary, Comorbidity_uCCI, Persistant_bacteremia, MLST) %>% left_join(significant_sample_df, by = c('original_sample_name' = 'sample_name'))
joined_df %<>% mutate(Sex_binary = Sex_binary -1)
joined_df %>% select(-c(original_sample_name)) %>% as.matrix %>% cor()

treewas_mortality <- read_excel(paste0(base_path, 'Set_28day_mortality_palliative_decision/treeWAS/iqtree/gene_treewas.xlsx'))
significant_mortality <- treewas_mortality %>% filter(terminal_pvalue<=0.05/nrow(treewas_mortality) | simultaneous_pvalue<=0.05/nrow(treewas_mortality) | subsequent_pvalue<=0.05/nrow(treewas_mortality))
significant_mortality2 <- treewas_mortality %>% filter(terminal_pvalue==0 | simultaneous_pvalue==0 | subsequent_pvalue==0)

sample_subset <- names(gene_matrix)[names(gene_matrix) %in% persistent_bacteremia$original_sample_name]
reduced_gene_matrix <- gene_matrix %>% select(Gene, all_of(sample_subset))
informative_genes <- 1:nrow(reduced_gene_matrix) %>% lapply(function(i){
  return.value <- NA
  matrix.row <- gene_matrix[i, ]
  if (length(table(matrix.row %>% select(-Gene) %>% unlist)) > 1){
    return.value <- matrix.row %>% pluck('Gene')
    } 
  return(return.value)
}) %>% unlist()
reduced_gene_matrix %<>% filter(Gene %in% informative_genes)

write_tsv(reduced_gene_matrix, '/Volumes/data/MPV/LEBC/persistent_bacteremia_reduced_pres.Rtab')
write_tsv(persistent_bacteremia %>% select(original_sample_name, Persistant_bacteremia), '/Volumes/data/MPV/LEBC/bacteremia/phenotype.tsv')
persistent_bacteremia %>% head()

pyseer_results <- read_tsv("/Volumes/data/MPV/LEBC/bacteremia/persistent_bacteremia_pyseer.txt")
pyseer_results %>% arrange(`filter-pvalue`) %>% head()

significant_genes$ID %in% (pyseer_results %>% arrange(`filter-pvalue`) %>% head(10) %>% pluck('variant'))

michele_output_gwas <- read_delim('/Users/B246357/ssi_stuff/2/feature_importance_gwas.csv', delim = ' ')
michele_output_gwas %>% filter(!is.na(shap_score)) %>% arrange(desc(shap_score))

