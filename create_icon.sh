#!/bin/bash

# Create basic PNG icon using printf and base64
# This creates a minimal 48x48 purple PNG icon

# Base64 encoded 48x48 purple PNG
ICON_B64="iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFYSURBVGiB7ZoxTsNAEEWfkQskCgoKKipq6igpqalp6Whp6ehoaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlp"

# Function to create PNG for each density
create_icon() {
    local size=$1
    local density=$2
    
    # Create basic colored rectangle as PNG
    printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00'"$(printf %02x $size)"'\x00\x00\x00'"$(printf %02x $size)"'\x08\x02\x00\x00\x00' > "app/src/main/res/mipmap-$density/ic_launcher.png"
    printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00'"$(printf %02x $size)"'\x00\x00\x00'"$(printf %02x $size)"'\x08\x02\x00\x00\x00' > "app/src/main/res/mipmap-$density/ic_launcher_round.png"
}

# Create icons for different densities
create_icon 36 mdpi
create_icon 48 hdpi  
create_icon 72 xhdpi
create_icon 96 xxhdpi
create_icon 144 xxxhdpi
