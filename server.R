#
# This is the server logic of a Shiny web application. You can run the 
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

plot_XY <- function(company_ls, X='date_published', Y='num_reactions', env=.GlobalEnv, ...) {
    for (i in 1:length(company_ls)) {
        temp_comp <- get(company_ls[i], envir = env)
        
        if (i == 1) {
            plot(temp_comp[,X], temp_comp[,Y], col=i, ..., xlab=X, ylab=Y)
        } else {
            points(temp_comp[,X], temp_comp[,Y], col=i)   
        }
    }
    legend("topright", legend=company_ls, fill=1:length(company_ls))
    
}

plot_hist <- function(company_ls, X='num_likes', ...) {
    for (i in 1:length(company_ls)) {
        if (i == 1) {
            hist(get(company_ls[i])[,X], col=i, density=10, ..., xlab=X)
        } else {
            hist(get(company_ls[i])[,X], col=i, add=TRUE, density=10, ...)
        }
    }
    legend("topright", legend=company_ls, fill=1:length(company_ls))
}


library(shiny)
library(ggplot2)


## Get time of day from UNIX time value
time_of_day <- function(val) {
    temp <- as.POSIXct(val, origin="1970-01-01")
    hours <- as.numeric(substr(temp, start=12, stop=13))
    minutes <- as.numeric(substr(temp, start=15, stop=16))/60
    seconds <- as.numeric(substr(temp, start=18, stop=19))/60/60
    
    return(hours + minutes + seconds)
}

## Get day of week from UNIX time value
day_of_week <- function(val) {
    return(weekdays(as.POSIXct(val, origin="1970-01-01")))
}

combine_all <- function(company_ls) {
    ## Combine all data into single data.frame
    full_dat <- data.frame()
    for (i in 1:length(company_ls)) {
        full_dat <- rbind(full_dat, cbind(get(company_ls[i]), Label=company_ls[i], row.names=NULL), row.names=NULL)
    }
    return(full_dat)
}

read_data <- function(socialmedia="facebook") {
    ## Read Data
    all_companies <- c("statefarm","allstate","geico","libertymutual","progressive","flotheprogressivegirl","nationwideinsurance")
    dir_contents <- list.files('test_data/')
    current_companies <- c()
    
    for (i in 1:length(all_companies)) {
        
        ## Read Instagram data
        if (socialmedia=="instagram") {
            current <- paste0(all_companies[i], "_insta")
            csv_name <- paste0(all_companies[i],"_instagram_metadata.csv")
        }
        ## Read Facebook data
        if (socialmedia=="facebook") {
            current <- paste0(all_companies[i], "_fbook")
            csv_name <- paste0(all_companies[i],"_facebook_statuses.csv")
        }
        
        if (csv_name %in% dir_contents) {
            temp <- read.csv(paste0('test_data/',csv_name), head=T, sep=",")
            if ('date_published' %in% names(temp)) {
                temp$hour_of_day <- unlist(lapply(temp$date_published, time_of_day))
                temp$day_of_week <- unlist(lapply(temp$date_published, day_of_week))
            } else {
                temp$date_published <- as.numeric(as.POSIXct(temp$status_published))
                temp$hour_of_day <- unlist(lapply(temp$status_published, time_of_day))
                temp$day_of_week <- unlist(lapply(temp$status_published, day_of_week))
            }
            assign(current, temp, envir = .GlobalEnv)
            current_companies <- c(current_companies, current)
        }
    }
    #current_companies <- unique(current_companies)
    assign('current_companies', unique(current_companies), envir=.GlobalEnv)
    
}


read_data('facebook')
full_dat <- combine_all(current_companies)


# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  
    # read_data("facebook")
    
    ranges <- reactiveValues(x = NULL, y = NULL)
    company_ls <- reactive({ sapply(input$companies, function(i) paste0(i, "_fbook")) })
    current_dat <- reactive({
        if (input$searchButton & input$search!="") {
            keep_index1 <- grep(input$search, full_dat$status_message, ignore.case=T, fixed=F, value=F)
            keep_index2 <- which(full_dat$Label %in% company_ls())
            full_dat[intersect(keep_index1, keep_index2), ]
        } else {
            subset(full_dat, Label %in% company_ls() )
        }
    })
    
    
    
    output$plot1 <- renderPlot({
        if (input$type == "time series") {
            ggplot(data=current_dat(), aes_string(x='date_published', y=input$statistic, group='Label', colour='Label')) +
                geom_point() + 
                coord_cartesian(xlim = ranges$x, ylim = ranges$y)
        } else if (input$type == "frequency") {
            if (input$by == "all") {
                ggplot(data=current_dat(), aes_string(x=input$statistic, fill='Label')) + geom_density(alpha=.3) + 
                    coord_cartesian(xlim = ranges$x, ylim = ranges$y)
            } else if (input$by == "day_of_week") {
                p <- ggplot(data = current_dat(), aes_string(x="day_of_week", y=input$statistic)) + geom_boxplot(aes(fill=Label))
                p + facet_wrap( ~ day_of_week, scales="free") + 
                    coord_cartesian(xlim = ranges$x, ylim = ranges$y)
            } else if (input$by == "hour_of_day") {
                ggplot(data=current_dat(), aes_string(x='hour_of_day', y=input$statistic, group='Label', colour='Label')) +
                    geom_point() + 
                    coord_cartesian(xlim = ranges$x, ylim = ranges$y)
            }
        }
    
    })
  
    output$cor_summary <- renderTable({
      cor(get(company_ls()[1], envir = .GlobalEnv)[,c(7,8,9)], use="pairwise.complete.obs")
    })
  
    env <- environment()
  
    if (FALSE) {
        output$summary <- renderPrint({
      n_temp <- dim(statefarm_fbook)[1]
      str(list('total posts'=n_temp,
               'has shares'=sum(!is.na(statefarm_fbook$num_shares) & statefarm_fbook$num_shares!=0) / n_temp,
               'has reactions'=sum(!is.na(statefarm_fbook$num_reactions) & statefarm_fbook$num_reactions!=0) / n_temp,
               'has comments'=sum(!is.na(statefarm_fbook$num_comments) & statefarm_fbook$num_comments!=0) / n_temp
               ))
  })
      
    }
    
    output$info <- renderPrint({
        if (input$type == "time series") {
            xvar = "date_published"
        } else if (input$by == "hour_of_day") {
            xvar = "hour_of_day"
        } else if (input$by == "day_of_week") {
            xvar = "hour_of_day"    
        }
      brushedPoints(current_dat(), input$plot1_brush,
                    xvar = xvar, yvar = input$statistic)  
  })
  
    observeEvent(input$plot1_dblclick, {
      brush <- input$plot1_brush
      if (!is.null(brush)) {
          ranges$x <- c(brush$xmin, brush$xmax)
          ranges$y <- c(brush$ymin, brush$ymax)
          
      } else {
          ranges$x <- NULL
          ranges$y <- NULL
      }
    })
  
    
    
    output$summary <- renderPrint({ dim(current_dat()) })
    
    eventReactive(input$updateButton, {
        system('python Facebook_scraper.py statefarm')
        read_data("facebook")
    })
    
})







