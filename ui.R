#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

library(shiny)


all_companies <- c("statefarm","allstate","geico","libertymutual","progressive","flotheprogressivegirl","nationwideinsurance")


# Define UI for application that draws a histogram
shinyUI(fluidPage(theme = "bootstrap.css", 
  
  # Application title
  titlePanel("Social Media Analytics"),
  
  plotOutput("plot1",
             dblclick = "plot1_dblclick",
             brush=brushOpts(id="plot1_brush", resetOnNew = TRUE)),
  fluidRow(column(12,verbatimTextOutput("info"))), 
  fluidRow(column(6,
                  tableOutput("cor_summary")),column(6,
                  verbatimTextOutput("summary"))
  ),
  hr(), 
  
  fluidRow(
    column(4, 
    checkboxGroupInput("companies", h4("Companies:"), 
                       choices = all_companies, selected="statefarm"),
    
    selectInput("socialmedia", h4("Social Media:"), choices=c("facebook")),
    
    actionButton("updateButton", "Update data")
    
    #dateRangeInput("dates", label = h4("Date range"))
    ),
    
    column(4,  
           dateRangeInput("dates", label = h4("Date range")),
           
           textInput("search", h4("Search filter:"), ""),
           
           actionButton("searchButton", "Search"), 
           
           selectInput("statistic", h4("Statistic of Interest:"), choices=c("num_reactions", "num_comments","num_shares"))
           
    ),
    column(4, selectInput("NLPcategory", h4("NLP category"), choices=c('All','1','2','3')),
           selectInput("type", h4("Type of Plot:"), choices=c("frequency", "time series")),
           
           
           conditionalPanel(
             condition = "input.type == 'frequency'",
             selectInput(
               "by", h4("By:"),
               c("all",
                 "hour_of_day",
                 "day_of_week"))
           )
    
  )
  
)))
