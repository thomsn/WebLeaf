# WebLeaf Notebooks for Data Science

These notebooks are run in google colab with the data being stored in google drive. They are
executed on T4 instances. The order in this readme is the order in which they are run
to produce a new model.

### WebLeafDataExport.ipynb
 - run locally on laptop
 - used to export the product page dataset to google drive
 - packs the HTML pages 100 at a time to reduce read requests
 - excludes non-English data because the text embedding model is english based

### WebLeafDataExploration.ipynb
 - Exploring the product page dataset
   - https://github.com/klarna/product-page-dataset
 - Experimenting with DOM crawling
 - Developing methods for maximizing text value capture 

### WebLeafData.ipynb
 - Converting the HTML pages into Text and Tag embeddings
 - Generating edge index's
 - Generating mask for elements without text values 
 - Storing tensors into chunks for efficient training loops
 - Saving meta data for the dataset 
 - Generating both the train and test data folders

### WebLeafDataValidation
 - Checking the output from WebLeafData.ipynb
 - Text validation 
 - Tree structure validation
 - Node Tag validation
 - Embedding Normalization validation

### WebLeafModel.ipynb
 - Model definition
   - GCN2Conv layers https://arxiv.org/pdf/2007.02133 
   - supposedly more performant at greater depths https://arxiv.org/pdf/2301.10536
 - training loop


### WebLeafValidation
 - final validation of the model 