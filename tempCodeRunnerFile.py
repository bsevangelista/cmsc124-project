    console_frame.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        # Create a console Text widget and configure it to fill space
        self.console = tk.Text(console_frame, wrap=tk.WORD, state='disabled')
        self.console.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Add a vertical scrollbar
        console_scroll = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console.yview)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=console_scroll.set)
        
        # Adjust row weights in the grid to make the console fill the remaining space
        self.main_frame.rowconfigure(4, weight=1)