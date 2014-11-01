#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
use Date::Calc;
#use Array::Utils qw(:all);
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# some globals used through the script
$debug = 0;
$students_dir = "./students";

if(defined param("user") && defined param("pass") && verified(param("user"), param("pass")) && !defined param("logout") && defined param("login")){
    %user_id = ();
    opendir(my $DIR, $students_dir);
    while(my $entry = readdir $DIR){
	next unless -d $students_dir . "/" . $entry;
	next if $entry eq "." or $entry eq "..";
	$user_id{$entry} = 0;
    }
    $i = 0;
    foreach my $user(sort keys %user_id){
	$user_id{$user} = $i++;
    }
    if(defined param("view_profile")){
	param("n", $user_id{param("view_profile")});
	print profile_screen();
    } elsif(defined param("find") && defined param("find_profile")){
	if(exists $user_id{param("find_profile")}){
    	    param("n", $user_id{param("find_profile")});
	    print profile_screen();
	} else {
	    print "<div class=\"alert alert-danger alert-dismissable\" role=\"alert\">",
		  "    User not found",
		  "</div>", "\n", 
		  home_screen();
	}
    } elsif(defined param("match") || defined param("match_page")){
	print match_screen();
    } else {
	print home_screen();
    }
} elsif(defined param("signup")){
    print signup_screen();
} elsif(defined param("create")){
    my $username = param("username_input");
    my $password = param("password_input");
    my $confirm = param("password_confirm");
    if ($username ne "" && $password ne "" && $confirm ne ""){
	if ($username =~ /[^a-zA-Z0-9]/){
	    print "<div class=\"alert alert-danger\" role=\"alert\">Invalid Username</div>", "\n";
            print signup_screen();
	} elsif (-d "students/$username"){
            print "<div class=\"alert alert-danger\" role=\"alert\">Username taken</div>", "\n";
            print signup_screen();
	} elsif ($password ne $confirm){
            print "<div class=\"alert alert-danger\" role=\"alert\">Passwords do not match</div>", "\n";
            print signup_screen();
	} else {
	    create_account($username, $password);
            print "<div class=\"alert alert-success\" role=\"alert\">Account created</div>", "\n";
	    print login_screen();
	}
    } else {
        print "<div class=\"alert alert-danger\" role=\"alert\">Please fill in all fields</div>", "\n";
	print signup_screen();
    }
} else {
    print login_screen();
}	

print page_trailer();
exit 0;	

sub verified {
    my $user = $_[0];
    my $pass = $_[1];
    if(-d "$students_dir/$user"){
	open F, "$students_dir/$user/profile.txt" or die "can not open$students_dir/$user/profile.txt: $!";
	while ($line = <F>){
	    if($line =~ /password:\s*$/){
		$realPass = <F>;
		$realPass =~ s/\s*//g;
		if($realPass eq $pass){
		    return 1;
		}
	    }
	}
    } 
    print "<div class=\"alert alert-danger\" role=\"alert\">Incorrect Username or Password</div>", "\n";
    return 0;
}

sub home_screen {
    if(defined param("page")){
  	if(defined param("next_page")){
	    $page = param("page") + 8;
	} elsif(defined param("prev_page")){
	    $page = param("page") - 8;
	}
    } else {
	$page = 0;
    }
    param("page", $page);
    my @users = ();
    opendir(my $DIR, $students_dir);
    while(my $entry = readdir $DIR){
	next unless -d $students_dir . "/" . $entry;
 	next if $entry eq "." or $entry eq "..";
	push @users, $entry;
    }
    @users = sort @users;
    @gallery = ();
    push @gallery, "<div align=center style=\"width:1100px\">";
    push @gallery, "<div class=\"row\">\n";
    for my $n ($page..$page + 7){
    	my $prof_pic = $students_dir . "/" . @users[$n] . "/profile.jpg";
	push @gallery, "    <div class=\"col-sm-6 col-md-3\">\n";
	push @gallery, "        <div class=\"thumbnail\">\n";
	push @gallery, "            <img src=$prof_pic>\n";
	push @gallery, "            <div class=\"caption\" align=\"left\">\n";
	push @gallery, "                <h3>$users[$n]</h3>\n";
	push @gallery, "                <p>Some Description.</p>\n";
	push @gallery, "                <p><button type=\"submit\" name=\"view_profile\" value=$users[$n] class=\"btn btn-primary\">View Profile</button></p>\n";
	push @gallery, "            </div>\n";
	push @gallery, "        </div>\n";
	push @gallery, "    </div>\n";
    }
    push @gallery, "</div>\n";
    push @gallery, "</div>\n";
    return  p, "\n",
    	    start_form(-method=>"GET"), "\n",
	    "<div class=\"container-fluid\" align=center>",
	    navigation(),
	    @gallery,
	    hidden("page"), "\n",
	    hidden("user"), "\n",
	    hidden("pass"), "\n",
	    hidden("login"), "\n",
	    "<ul class=\"pager\">", "\n",
	    "<li class\"previous\"><button type=\"submit\" name=\"prev_page\" class=\"btn btn-primary\" align=left>Prev</btn></li>", "\n",
	    "<li class=\"next\"><button type=\"submit\" name=\"next_page\" class=\"btn btn-primary\" align=right>Next</btn></li>", "\n",
	    "</ul>", "\n",
	    "</div>", "\n",
	    end_form, "\n",
	    p, "\n";
}

sub navigation {
    $user = param("user");
    return  "<nav class=\"navbar navbar-default\" role=\"navigation\">", "\n",
 	    "    <div>", "\n",
	    "        <table class=\"table\" align=center width=\"100%\">", "\n",
	    "            <tr valign=\"center\">", "\n",
	    "                <td width=\"33%\" align=\"right\"><span class=\"navbar-brand\">LOVE2041 <small><span class=\"glyphicon glyphicon-heart\"></span> Find yo bae.</small></span></td>", "\n",
	    "	             <td width=\"34%\" align=\"center\"><button type=\"submit\" name=\"match\" value=\"Match Me\" class=\"btn btn-danger\">Find my Soulmate</button></td>", "\n",
	    "	             <td width=\"23%\" align=\"center\">", "\n",
	    "                    <form class=\"navbar-form navbar-left\" role=\"search\">", "\n",
	    "                        <div class=\"input-group\" align=right style=\"width:300px; margin-left:auto; padding-top:8px\">", "\n",
	    "                            <input type=\"text\" name=\"find_profile\" class=\"form-control\" placeholder=\"Search\">", "\n",
	    "                            <span class=\"input-group-btn\"><button type=\"submit\" name=\"find\" value=\"find\" class=\"btn btn-default\">Search</button></span>", "\n",
	    "                        </div>", "\n",
	    "                    </form>", "\n",
	    "                </td>", "\n",
	    "                <td width=\"10%\"><div style=\"text-align:center\">Logged in as $user <button type=\"submit\" name=\"logout\" class=\"btn btn-primary\" align=right>Logout</btn></div></td>", "\n",
	    "            </tr>", "\n",
            "        </table>", "\n",
	    "    </div>", "\n",
	    "</nav>", "\n";
}

sub match_screen {
    my $user = param("user");
    
    my %my_pref = ();
    my %my_info = ();

    my $student_loc = "$students_dir/$user";

    open F, "$student_loc/preferences.txt" or die "can not open $student_loc/preferences.txt: $!";
    while($line = <F>){
  	if($line =~ /gender:/){
	    $line = <F>;
	    chomp $line;
	    $line =~ s/^\s*//g;
	    push (@{$my_pref{"gender"}}, $line);
	} elsif($line =~ /age:/){
	    for(0..1){	#once for min then again for max
		$line = <F>; $line = <F>;
		chomp $line;
		$line =~ s/^\s*//g;
		push (@{$my_pref{"age"}}, $line);
	    }
	} elsif($line =~ /hair_colours:/){
	    $line = <F>;
	    while($line =~ /^\s+/){
		chomp $line;
		$line =~ s/^\s*//g; 
		push (@{$my_pref{"hair"}}, $line);
		$line = <F>;
	    }
	} elsif($line =~ /height:/){
	    for(0..1){
		$line = <F>; $line = <F>;
                chomp $line;
                $line =~ s/^\s*//g;
                push (@{$my_pref{"height"}}, $line);
	    }
	} elsif($line =~ /weight:/){
            for(0..1){
                $line = <F>; $line = <F>;
                chomp $line;
                $line =~ s/^\s*//g;
                push (@{$my_pref{"weight"}}, $line);
            }
        }
    }
    close F;

    open F, "$student_loc/profile.txt" or die "can not open $student_loc/profile.txt: $!";
    my $n;
    while($line = <F>){
  	chomp $line;
        if($line =~ /\s*([^ ]*):\s*$/){
            $n = $1;
        } else {
            $line =~ s/^\s*//g;
	    $line =~ s/\s*$//g;
            push(@{$my_info{$n}}, $line);
        }
    }
    close F;

    if(!defined @{$my_pref{"gender"}}){
	push @{$my_pref{"gender"}}, "any"; #assume no gender pref
    }
    if(!defined @{$my_pref{"age"}}){
	my $age;
	if($my_info{"birthdate"}[0] =~ /([0-9]{2})\/([0-9]{2})\/([0-9]{4})/){
            $age = calc_age($1, $2 - 1, $3);
        } elsif($my_info{"birthdate"}[0] =~ /([0-9]{4})\/([0-9]{2})\/([0-9]{2})/) {
	    $age = calc_age($3, $2 - 1, $1);
	}
        push @{$my_pref{"age"}}, ((($age/2) + 7), (($age - 7) * 2)); #scientifically proven for min/max age
    }
    if(!defined @{$my_pref{"hair"}}){
        push @{$my_pref{"hair"}}, "any"; #assume they dont care
    }
    if(!defined @{$my_pref{"height"}}){
        push @{$my_pref{"height"}}, "any";
    }
    if(!defined @{$my_pref{"weight"}}){
        push @{$my_pref{"weight"}}, "any";
    }

    %scores = ();
    my @users = ();
    opendir(my $DIR, $students_dir);
    while(my $entry = readdir $DIR){
        next unless -d $students_dir . "/" . $entry;
        next if $entry eq "." or $entry eq ".." or $entry eq $user;
        push @users, $entry;
    }
    closedir $DIR;

    %my_movies = ();
    foreach (@{$my_info{"favourite_movies"}}){
	$my_movies{$_}++;
    }
    %my_books = ();
    foreach (@{$my_info{"favourite_books"}}){
	$my_books{$_}++;
    }
    %my_tv = ();
    foreach (@{$my_info{"favourite_TV_shows"}}){
        $my_tv{$_}++;
    }
    %my_hobbies = ();
    foreach (@{$my_info{"favourite_hobbies"}}){
        $my_hobbies{$_}++;
    }
    %my_bands = ();
    foreach (@{$my_info{"favourite_bands"}}){
        $my_bands{$_}++;
    }
    %my_courses = ();
    foreach (@{$my_info{"courses"}}){
        $my_courses{$_}++;
    }	

    foreach $candidate (@users){
	$student_loc = "$students_dir/$candidate";
	%their_info = ();
	open F, "$student_loc/profile.txt" or die "can not open $student_loc/profile.txt: $!";
        my $c;
        while($line = <F>){
            if($line =~ /\s*([^ ]*):\s*$/){
	        $c = $1;
	    } else { 
	        $line =~ s/^\s*//g;
		$line =~ s/\s*$//g;
	        push(@{$their_info{$c}}, $line);
	    }
	}
	close F;

	if($their_info{"gender"}[0] ne $my_pref{"gender"}[0] && $my_pref{"gender"}[0] ne "any"){
	    $scores{$candidate} = 0;
	    next;
	}

	$age_score = 0;		#/20
	$hair_score = 0;	#/20
	$height_score = 0;	#/20
	$weight_score = 0;	#/20

	my $age;
	if($their_info{"birthdate"}[0] =~ /([0-9]{2})\/([0-9]{2})\/([0-9]{4})/){
	    $age = calc_age($1, $2 - 1, $3);
	} elsif($their_info{"birthdate"}[0] =~ /([0-9]{4})\/([0-9]{2})\/([0-9]{2})/){
	    $age = calc_age($3, $2 - 1, $1);
	}
	
	if($age >= $my_pref{"age"}[0] && $age <= $my_pref{"age"}[1]){
	    $age_score = 20;
	} elsif($age > $my_pref{"age"}[1]){
	    $age_score = max(0, 20 - ($age - $my_pref{"age"}[1])*3); #-3 points for each year above 
	} else {
	    $age_score = max(0, 20 - ($my_pref{"age"}[0] - $age)*3); #-3 points for each year below 
	}

	if($my_pref{"hair"}[0] eq "any"){
	    $hair_score = 20;
	} elsif(defined $their_info{"hair_colour"}[0]){
	    foreach $colour (@{$my_pref{"hair"}}){
	  	if($their_info{"hair_colour"}[0] eq $colour){
	            $hair_score = 20;
		}
	    }
	}

	if($my_pref{"height"}[0] eq "any"){
	    $height_score = 20;
	} else {
	    if(defined $their_info{"height"}[0]){
	 	$t_height = ($their_info{"height"}[0] =~ s/\D//g);
	 	$min_height = ($my_pref{"height"}[0] =~ s/\D//g);
		$max_height = ($my_pref{"height"}[1] =~ s/\D//g);
		if($t_height >= $min_height && $t_height <= $max_height){
		    $height_score = 10;
		} elsif($t_height > $max_height){
		    $height_score = max(0, 20 - ($t_height - $max_height)*100);
		    #-1 point for every .01m above max
		} else {
		    $height_score = max(0, 20 - ($min_height - $t_height)*100);
		    #-1 point for every .01m below min
		}
	    } 
	} #no height specified = 0 points

	if($my_pref{"weight"}[0] eq "any"){
            $weight_score = 20;
        } else {
            if(defined $their_info{"weight"}[0]){
                $t_weight = ($their_info{"weight"}[0] =~ s/\D//g);
                $min_weight = ($my_pref{"weight"}[0] =~ s/\D//g);
                $max_weight = ($my_pref{"weight"}[1] =~ s/\D//g);
                if($t_weight >= $min_weight && $t_weight <= $max_weight){
                    $weight_score = 10;
                } elsif($t_weight > $max_weight){
                    $weight_score = max(0, 20 - ($t_weight - $max_weight)*2);
                    #-2 points for every 1kg above max
                } else {
                    $weight_score = max(0, 20 - ($min_weight - $t_weight)*2);
                    #-2 point for every  1kg below min
                }
	    }
        } #no weight specified = 0 points

	$scores{$candidate} = ($age_score + $hair_score + $height_score + $weight_score);

	$common_score = 0;
	foreach (@{$their_info{"favourite_movies"}}){
	    if (defined $my_movies{$_}){
		$common_score += 3;
	    }
	}
	foreach (@{$their_info{"favourite_books"}}){
            if (defined $my_books{$_}){
                $common_score += 3;
            }
        }
        foreach (@{$their_info{"favourite_TV_shows"}}){
            if (defined $my_tv{$_}){
                $common_score += 3;
            }
        }
        foreach (@{$their_info{"favourite_bands"}}){
            if (defined $my_bands{$_}){
                $common_score += 3;
            }
        }
        foreach (@{$their_info{"favourite_hobbies"}}){
            if (defined $my_hobbies{$_}){
                $common_score += 5;
            }
        }
        foreach (@{$their_info{"courses"}}){
            if (defined $my_courses{$_}){
                $common_score += 1;
            }
        }
	if(defined($their_info{"degree"}[0]) && defined($my_info{"degree"}[0]) &&$their_info{"degree"}[0] eq $my_info{"degree"}[0]){ $common_score += 5;}

	$scores{$candidate} += $common_score;
    }

    foreach $candidate (keys %scores){
	if($scores{$candidate} < 60){
	    delete($scores{$candidate});
	}
    }

    @soulmates = sort {$scores{$b} <=> $scores{$a}} keys(%scores);
    @table = ();
    foreach(@soulmates){
	push @table, "<tr><td align=\"right\"><button class=\"btn btn-primary btn-sm\" type=\"submit\" name=\"view_profile\" value=\"$_\">$_</button></td><td align=\"left\">$scores{$_}</td></tr>\n";
    }

    my $page = param("match_page") || 0;
    if(defined param("match_next")){
        if($page + 10 <= $#soulmates){
            $page = $page + 10
	} else {
            $page = $#soulmates;
        }
    } elsif(defined param("match_prev")) {
        $page = $page - 10 if($page - 10 >= 0);
    } else {
	$page = 0;
    }

    param("match_page", $page);
    $page_end = $page + 9;

    @to_show = ();
    for my $n($page..$page_end){
	push @to_show, $table[$n];
    }

    return  p,
	start_form(-method=>"GET"), "\n",
	"<div class=\"container-fluid\" align=center>", "\n",
	navigation(),
	"<h1>", scalar @soulmates, " Matches Found</h1>", "\n",
	"<table class=\"table table-striped\" style=\"width:750px\">", "\n",
	"<col align=\"left\"><col align=\"right\">", "\n",
	"<tr><th style=\"text-align:right\">Username</th><th>Compatibility Score</th></tr>", "\n",
	@to_show,
	"</table>", "\n",
	"<button type=\"submit\" class=\"btn btn-primary\" name=\"match_prev\">Prev</button>", "\n",
	"<button type=\"submit\" class=\"btn btn-primary\">Return</button>", "\n",
	"<button type=\"submit\" class=\"btn btn-primary\" name=\"match_next\">Next</button>", "\n",
	"</div>", "\n",
	end_form(), "\n",
	hidden("user"), "\n",
	hidden("pass"), "\n",
	hidden("match_page"), "\n",
	hidden("login"), "\n",
	p, "\n";
}

sub login_screen {
    return  p, "\n",
	    start_form(-method=>"POST"), "\n",
	    "<div class=\"container\" align=center style=\"margin-top:25vh\">", "\n",
	    "<h1>LOVE2041<small><br>Find yo bae.</small></h1>", "\n",
	    "    <div style=\"width:500px; margin-top:50px\" align=center>", "\n",
	    "        <div>", "\n",
	    "            <div class=\"input-group input-group-lg\" style=\"margin-bottom:10px\">", "\n",
	    "                <span class=\"input-group-addon\"><span class=\"glyphicon glyphicon-user\"></span></span>", "\n",
	    "                <input type=\"text\" class=\"form-control\" placeholder=\"Username\" name=\"user\">", "\n",
	    "            </div>", "\n",
	    "            <div class=\"input-group input-group-lg\" style=\"margin-bottom:10px\">", "\n",
	    "                <span class=\"input-group-addon\"><span class=\"glyphicon glyphicon-lock\"></span></span>", "\n",
	    "                <input type=\"password\" class=\"form-control\" placeholder=\"Password\" name=\"pass\">", "\n",
	    "            </div>", "\n",
	    "        </div>", "\n",
	    "        <div>", "\n",
	    "            <button type=\"submit\" name=\"login\" class=\"btn btn-success btn-lg\"><span class=\"glyphicon glyphicon-log-in\"></span></button>", "\n",
	    "        </div>", "\n",
	    "        <div style=\"margin:20px\">", "\n",
	    "            <h4><small>Don't have an account?</small></h4>", "\n",
	    "            <button type=\"submit\" name=\"signup\" class=\"btn btn-primary\">Sign Up</button>", "\n",
            "        </div>", "\n",
	    "    </div>", "\n",
	    "</div>", "\n",
	    end_form, "\n",
	    hidden("user"),
	    hidden("pass"),
	    p, "\n";
}

sub signup_screen {
    return  p, "\n",
	start_form(-method=>"GET"), "\n",
	"<div class=\"container\" align=center style=\"margin-top:25vh\">", "\n",
        "<h1>LOVE2041<small><br>Find yo bae.</small></h1>", "\n",
        "    <div style=\"width:500px; margin-top:50px\" align=center>", "\n",
	"        <form class=\"form-horizontal\" role=\"form\">", "\n",
	"            <div class=\"form-group\">", "\n",
	"                <label for=\"username_input\" class=\"col-sm-2 control-label\">Username</label>", "\n",
	"		 <div class=\"col-sm-10\" style=\"margin-bottom:10px\">", "\n",
	"		     <input type=\"text\" class=\"form-control\" name=\"username_input\" id=\"username_input\" placeholder=\"Username\">", "\n",
	"		 </div>", "\n",
	"            </div>", "\n",
        "            <div class=\"form-group\">", "\n",
        "                <label for=\"password_input\" class=\"col-sm-2 control-label\">Password</label>", "\n",
        "                <div class=\"col-sm-10\" style=\"margin-bottom:10px\">", "\n",
        "                    <input type=\"password\" class=\"form-control\" name=\"password_input\" id=\"password_input\" placeholder=\"Password\">", "\n",
        "                </div>", "\n",
        "            </div>", "\n",
        "            <div class=\"form-group\">", "\n",
        "                <label for=\"password_confirm\" class=\"col-sm-2 control-label\">Confirm Password</label>", "\n",
        "                <div class=\"col-sm-10\" style=\"margin-bottom:10px\">", "\n",
        "                    <input type=\"password\" class=\"form-control\" name=\"password_confirm\" id=\"password_confirm\" placeholder=\"Confirm Password\">", "\n",
        "                </div>", "\n",
        "            </div>", "\n",
        "        </form>", "\n",
	"	 <div align=center>", "\n",
        "            <button type=\"submit\" name=\"create\" class=\"btn btn-primary\">Create Account</button>", "\n",
	"	 </div>", "\n",
        "    </div>", "\n",
        "</div>", "\n",
	end_form, "\n",
	hidden("username_input");
	hidden("password_input");
	hidden("password_confirm");
	p, "\n";
}

sub create_account(){
    my($username, $password) = @_;
    mkdir "students\/$username" or die "Could not make dir students/$username: $!";
    my $profile = "students\/$username\/profile.txt";
    open FILE, '>'.$profile or die "Could not open $profile: $!";
    print FILE "username:\n";
    print FILE "	$username\n";
    print FILE "password:\n";
    print FILE "	$password\n";
    close FILE;
    my $preferences = "students\/$username\/preferences.txt";
    open FILE, '>'.$preferences or die "Could not open $preferences: $!";
    close FILE;
}

sub profile_screen {
    my $n = param('n') || 0;
    my @students = glob("$students_dir/*");
    $n = min(max($n, 0), $#students);
    my $student_to_show  = $students[$n];
    my $profile_filename = "$student_to_show/profile.txt";
    open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
    %details = ();
    while($line = <$p>){
	chomp $line;
	if($line =~ /\s*([^ ]*):\s*$/){
 	    $n = $1;
	} else {
	    $line =~ s/^\s*//;
	    push(@{$details{$n}}, $line);
	}
    }
    close $p;
    $prof_pic_loc = "$student_to_show/profile.jpg";

    %photos = ();
    opendir(my $DIR, $student_to_show) or die "cannot open dir $student_to_show: $!";
    while(my $entry = readdir $DIR){
        next if($entry !~ /^photo[0-9]+\./);
        $photos{$entry}++;
    }
    closedir $DIR;

    @gallery = ();
    foreach $photo (keys %photos){
        push @gallery, "<img src=$student_to_show/$photo class=\"img-thumbnail\" style=\"margin-bottom:5px\">\n";
    }

    $student_to_show =~ s/^\.\/students\///;
    $birthdate = $details{"birthdate"}[0];
    my $age;
    if($birthdate =~ /([0-9]{2})\/([0-9]{2})\/([0-9]{4})/){
	$age = calc_age($1, $2 - 1, $3);
    } elsif ($birthdate =~ /([0-9]{4})\/([0-9]{2})\/([0-9]{2})/){
	$age = calc_age($3, $2 - 1, $1);
    }
    my $degree = $details{"degree"}[0];

    @bio = ();
    push @bio, "<tr><td>Age</td><td>$age</td></tr>\n";
    push @bio, "<tr><td>Gender</td><td>" . ucfirst($details{"gender"}[0]) . "</td></tr>\n";
    push @bio, "<tr><td>Degree</td><td>" . ucfirst($details{"degree"}[0]) . "</td></tr>\n";
    if (defined $details{"hair_colour"}[0]){
        push @bio, "<tr><td>Hair</td><td>" . ucfirst($details{"hair_colour"}[0]). "</td></tr>\n";
    } else {	
        push @bio, "<tr><td>Hair</td><td>Unknown</td></tr>\n";
    }
    if (defined $details{"height"}[0]){
        push @bio, "<tr><td>Height</td><td>" . $details{"height"}[0]. "</td></tr>\n";
    } else {
        push @bio, "<tr><td>Height</td><td>Unknown</td></tr>\n";
    }
    if (defined $details{"weight"}[0]){
        push @bio, "<tr><td>Weight</td><td>" . $details{"weight"}[0]. "</td></tr>\n";
    } else {
        push @bio, "<tr><td>Weight</td><td>Unknown</td></tr>\n";
    }
 
    @about = ();
    push @about, "<tr><td>Favourite Movies</td><td>\n";
    foreach $movie (@{$details{"favourite_movies"}}){
	push @about, "$movie <br>\n";
    }
    push @about, "</td></tr>\n";

    push @about, "<tr><td>Favourite Shows</td><td>\n";
    foreach $show (@{$details{"favourite_TV_shows"}}){
        push @about, "$show <br>\n";
    }
    push @about, "</td></tr>\n";

    push @about, "<tr><td>Favourite Books</td><td>\n";
    foreach $book (@{$details{"favourite_books"}}){
        push @about, "$book <br>\n";
    }
    push @about, "</td></tr>\n";

    push @about, "<tr><td>Favourite Bands</td><td>\n";
    foreach $band (@{$details{"favourite_bands"}}){
        push @about, "$band <br>\n";
    }
    push @about, "</td></tr>\n";

    push @about, "<tr><td>Favourite Hobbies</td><td>\n";
    foreach $hobby (@{$details{"favourite_hobbies"}}){
        push @about, "$hobby <br>\n";
    }
    push @about, "</td></tr>\n";

    return  p, "\n",
	    start_form(-method=>"POST"), "\n",
	    "<div class=\"container-fluid\" align=center>", "\n",
	    navigation(),
	    "<div class=\"jumbotron\" align=\"center\">", "\n",
	    "    <img class=\"img-circle\" src=$prof_pic_loc>", "\n",
	    "    <h2>$student_to_show</h2>", "\n",
	    "</div>", "\n",
	    "<div class=\"container\" align=center>", "\n",
	    "    <h3>Gallery<h3>", "\n",
	    @gallery,
	    "</div>", "\n",
	    "<table style=\"width:1000px\" align=center>", "\n",
	    "    <td width=35% valign=top>", "\n",
	    "        <h3 align=center>Bio</h3>", "\n",
	    "        <table class=\"table table-striped\" style=\"width:475px\" align=center", "\n",
	    @bio,
	    "        </table>", "\n",
	    "    </td>", "\n",
	    "    <td width=65% valign=top>", "\n",
	    "        <h3 align=center>About</h3>", "\n",
            "        <table class=\"table table-striped\" style=\"width:475px\" align=center>", "\n",
	    @about,
            "        </table>", "\n",
	    "    </td>", "\n",
	    "</table>", "\n",
	    "<button type=\"submit\" class=\"btn btn-primary\">Return</button>", "\n",
	    "</div>", "\n",
	    hidden("user"), "\n",
	    hidden("pass"), "\n",
	    hidden("login"), "\n",
	    end_form, "\n",
	    p, "\n";
}

#
# HTML placed at bottom of every screen
#
sub page_header {
    return header,	
           start_html("-title"=>"LOVE2041",
 -head => [ Link( { -rel => 'stylesheet', -type => 'text/css', -href => "https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css"}), ]);
}

#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

sub calc_age {
    my ($bday, $bmonth, $byear) = @_;
    my ($day, $month, $year) = (localtime)[3..5];
    $year += 1900;

    my $age = $year - $byear;
    $age-- unless sprintf("%02d%02d", $month, $day)
		>=sprintf("%02d%02d", $bmonth, $bday);
    return $age;
}
