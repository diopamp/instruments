"""
Some useful functions
This module shouldn't contain anything equipments, like GPIB or serial functions
"""
import smtplib
import ConfigParser
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy import stats

def twoscomplement(int_in, bitsize):
    """
    Compute two's complement
    http://stackoverflow.com/a/1604701/1527875
    """
    return int_in - (1 << bitsize)
        
def split_string(str_in, stepsize):
    """
    Split a string every N charaters and store into an array 
    """
    str_out = [str_in[ii:ii+stepsize] for ii in range(0, len(str_in), stepsize)]
    return str_out
    

def write_data_n1(filename, arr1):
    """
    Write data to N-by-1 array
    """
    f = open(filename, 'w')
    for ii in range(len(arr1)):
        f.write('%s\n' % str(arr1[ii]))
    f.close()
    
def write_data_n2(filename, arr1, arr2, ftype='ef'):
    """
    Write data to N-by-2 array
    """
    f = open(filename, 'w')
    for ii in range(len(arr1)):
        #f.write('%s\t%s\n' % (str(arr1[ii]), str(arr2[ii])))
        if ftype.lower() == 'ef':
            f.write('%e\t%f\n' % (arr1[ii], arr2[ii]))
        elif ftype.lower() == 'ee':
            f.write('%e\t%e\n' % (arr1[ii], arr2[ii]))
        elif ftype.lower() == 'fe':
            f.write('%f\t%e\n' % (arr1[ii], arr2[ii]))
        elif ftype.lower() == 'ff':
            f.write('%f\t%f\n' % (arr1[ii], arr2[ii]))
    f.close()
   
def write_data_n3(filename, arr1, arr2, arr3):
    """
    Write data to N-by-3 array
    """
    f = open(filename, 'w')
    for ii in range(len(arr1)):
        f.write('%e\t%f\t%f\n' % (arr1[ii], arr2[ii], arr3[ii]))
    f.close()

def append_to_file_n2(filename, x1, x2, str_format):
    """
    Write to file in append mode; will not overwrite existing content
    """
    f = open(filename, 'a')
    if str_format == 'fe':
        f.write('%f\t%e\n' % (x1, x2))
    elif str_format == 'ff':
        f.write('%f\t%f\n' % (x1, x2))
    elif str_format == 'ss':
        f.write('%s\t%s\n' % (x1, x2))
    f.close()

def iprint(msg, verbose=True):
    """
    Add a on/off switch to print: when verbose is False, do nothing; when verbose is True, print as mormal
    """
    if verbose:
        print msg
    else:
        pass


def str2list(s):
    # Helper function for sendemail()
    # If input is a string, convert it to list.
    # If it is a list, keep it as is
    if type(s) is str:
        return [s]
    elif type(s) is list:
        return s
    else:
        print 'Input is neither str nor list. Something is wrong...'
        sys.exit(2)

def sendemail(to, subject, body, **kwargs):
    """
    Send email in Python
    Input args:
        to: destination email address(es), a string or a string list
        **kwargs, optional args: 
            cc: CC address(es), a string or a string list
            bcc: BCC address(es), a string or a string list
            profile: choose a profile in rcfile, a string; the default is 'aim'
            rcfile: the path for rcfile, a string; an example of rcfile is available at https://gist.github.com/vadiode/7076973#file-sendemailrc
    Examples:
    send_email('user1@example.com', 'Test', 'This is a test'); 
    send_email('user1@example.com', 'Test', 'This is a test', profile='aim'); 
    send_email('user1@example.com', 'Test', 'This is a test', cc=['user2@example.com', 'user3@example.com'], bcc=['user3@example.com']);
    """
    # Default values
    to = str2list(to)
    cc = []
    bcc = []
    profile = 'aim'
    rcfile = '/home/ll3kx/.sendemailrc'
    
    for key, val in kwargs.iteritems():
        if key == 'cc':
            cc = str2list(val)
        elif key == 'bcc':
            bcc = str2list(val)
        elif key == 'rcfile':
            if not (type(val) is str):
                print 'rcfile should be str type'
                sys.exit(2)
            else: 
                rcfile = val
        elif key == 'profile':
            if not (type(val) is str):
                print 'profile should be str type'
                sys.exit(2)
            else: 
                profile = val
       
    config = ConfigParser.ConfigParser()
    config.read(rcfile)

    if not(profile in config.sections()):
        print 'Profile not in the configuration. Exiting...'
        sys.exit(2)
    
    sender= config.get(profile, 'from')
    username = config.get(profile, 'username')
    password = config.get(profile, 'password')
    smtphost = config.get(profile, 'smtphost')
    
    msg = '\r\n'.join([
          "From: %s" % sender, 
          "To: %s" % ','.join(to),
          "CC: %s" % ','.join(cc),
          "BCC: %s" % ','.join(bcc), 
          "Subject: %s" % subject,
          "",
          body])
    #print msg
    server = smtplib.SMTP(smtphost)
    server.login(username, password)
    server.sendmail(sender, to+cc+bcc, msg)
    server.quit()
    
def plot_lfn_data(filename):
    """
    Plot the LFN data given the data filename
    """
    d = np.loadtxt(filename)
    plt.loglog(d[:, 0], d[:, 1])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Noise')
    plt.title(filename)
    plt.savefig(filename+'.png')

def osc_time_shift(infile, outfile=None):
    """
    A helper function to reorganize the data read from an oscilloscope
    The result contains a time grid with t=0 as the first point
    Input: Data file containing an N-by-2 matrix, with the first column as time axis
    """

    d = np.loadtxt(infile)
    if not outfile:
        outfile = infile+'.out'

    t = d[:, 0]
    y = d[:, 1]

    dt = t[1] - t[0]
    T = t[-1] - t[0] + dt
    ind = np.where(t >= 0)   # is a tuple containing np.array type
    ind = ind[0]

    if ind[0] == 0:
        t2 = t
        y2 = y
    else:
        t_pt1 = t[ind]
        t_pt2 = t[0:ind[0]] + T
        y_pt1 = y[ind]
        y_pt2 = y[0:ind[0]]
        t2 = np.concatenate((t_pt1, t_pt2), axis=0)
        y2 = np.concatenate((y_pt1, y_pt2), axis=0)

    N = t2.__len__()
    np.savetxt(outfile, np.concatenate((t2.reshape(N,1), y2.reshape(N,1)), axis=1), fmt='%e')
    #plt.plot(t2, y2)
    #plt.show()


def rtd(resistance):
    """
    Convert the RTD resistance reading to temperature (unit: K)
    The reference curve is obtained from US Sensors
    Pt RTD model #: PPG102A6; manufacturer: US Sensors
    """
    tb = np.loadtxt('files/RTD_Pt1000_table.asc')
    temperature = np.interp(resistance, tb[:,0], tb[:,1])
    return temperature


def down_sampling(data, down_sampling_factor=0.1):
    """
    Down-sampling the input data by a factor
    """
    num_pts = len(data)
    x = np.linspace(1,num_pts, num_pts)
    x2 = np.linspace(1, num_pts, np.floor(num_pts*down_sampling_factor))
    return np.interp(x2, x, data)


def fft_ss(data, fs, **kwargs):
    """
    Compute the single-sided FFT spectrum
    yfft, f = fft_ss(data, fs, **kwargs)
    yfft, f = fft_ss(data, fs, output_type='rmspower')
    Input args:
    * data: data to be FFT'ed
    * fs: sampling rate
    * **kwargs: output_type (either "amplitude" (default) or "rmspower")
    Example:
    * y, f = fft_ss(data, fs)
    * y,f = fft_ss(data, fs, output_type='rmspower')
    """
    output_type = 'amplitude'    # default output type
    for key,value in kwargs.iteritems():
        if key.lower() == 'output_type':
            output_type = value

    Ns = len(data)
    yf = np.fft.fft(data)
    ff = float(fs)/Ns * np.arange(Ns)

    # Compute the single-sided FFT amplitude spectrum
    # Note that the first point of yf is DC value (f==0), and the rest point are symmetrical w.r.t. point Ns/2
    y_ind_end = int(np.floor(Ns/2))
    f = ff[0:(y_ind_end + 1)]
    yfft = yf[0:(y_ind_end + 1)]

    # Renormalization
    # The first point is DC value; normalize it by Ns
    # Other points are the addition of double-sided spectrum; normalize them by (Ns/2)
    yfft[0] = yfft[0]/Ns
    yfft[1:(y_ind_end + 1)] = yfft[1:(y_ind_end + 1)]/Ns*2.0

    if output_type.lower() == 'amplitude':
        y = np.abs(yfft)
    elif output_type.lower() == 'rmspower':
        # Remember DC power should not be divided by 2 like RMS AC power
        y = np.abs(yfft)**2
        y[1:(y_ind_end + 1)] = y[1:(y_ind_end + 1)]/2.0
    return y, f


def fft_pro(filename, fs, N_avg, ratio_overlap, **kwargs):
    """
    Get single-sided FFT power density spectrum from a time trace, with averaging
    The idea is to reuse part of the previous unit trace for the next FFT
    Input args:
    * filename: input data filename
    * fs: sampling rate
    * N_avg: number of averaging traces
    * ratio_overlap: ratio of reused points for each trace
    Example:
    * power_density, f = fft_pro('test.dat', 5e4, 1000, 0.99)
    """
    plot = False  # default not plotting
    for key,value in kwargs.iteritems():
        if key == 'plot':
            plot = bool(value)
            

    d = np.loadtxt(filename)
    path_str, basename = os.path.split(filename)
    name_str, ext_str = os.path.splitext(basename)

    N_tot = len(d)
    p = 1.0 - ratio_overlap
    N_unit = int(np.floor(N_tot/(1 + p*(N_avg -1))))  # calculate the unit trace length
    N_new  = int(np.floor(p*N_unit))

    if N_new == 0:
        raise ValueError('Overlapping ratio too large')

    tmp = 0
    for ii in range(N_avg):
        #print ii
        d_ind_start = N_new * ii
        unit_trace = d[d_ind_start:(d_ind_start+N_unit)]
        y, f = fft_ss(unit_trace, fs, output_type='rmspower')
        tmp = tmp + y
    power_fft = tmp/N_avg
    df = f[1] - f[0]
    power_density = power_fft/df

    if plot:
        plt.figure(119)
        plt.loglog(f, power_density)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('RMS power (V^2/Hz)')
        plt.title(name_str)
        plt.savefig(name_str+'.png')     
           
    write_data_n2('fft_'+name_str+'.dat', f, power_density, ftype='ee')
    return power_density, f


def iv_merger(filename_root):
    """
    Merge the IV characteristics data based on file names. The file name should be something like 'dev1_0.dat'
    For example, for files 'dev1_0.dat', 'dev1_1.dat', 'dev1_2.dat', this function reads these data, merge them together,
    sort according to voltage (the first column in the data), and return the result in two float arrays. Also, a file
    called 'dev1_IV.dat' is also created under the same directory.
    Input arg: filename_root; for the example above, it is 'dev1'
    """
    V = []
    I = []
    for df in glob.glob('%s*.dat' % filename_root):
        data = np.loadtxt(df)
        V.extend(data[:, 0].tolist())
        I.extend(data[:, 1].tolist())    # convert the numpy array type to list type (to use str.extend() method)
    V2 = np.array(V)
    I2 = np.array(I)
    ind = np.argsort(V2)    # return a sorted index (a numpy array); in other words, V2[ind] is the sorted array
    write_data_n2('%s_IV.dat' % filename_root, V, I, ftype='fe')
    return V2[ind].tolist(), I2[ind].tolist()   # eventually return a common list type

def flicker_calc(f_in, P_in, f0, **kwargs):
    """
    Calculate the flicker noise slope, and power density at the designated frequency
    Usage: 
    beta, P0 = flicker_calc(f_in, P_in, f0, **kwargs)
    Input args:
    * f_in: frequency; an array
    * P_in: y axis data; an array
    * f0: calculate the fitted P in f0; float type
    * (optional) plot: whether to plot the data; boolean type 
    Output args: 
    * beta: fitted flicker slope
    * P0: fitted P in f0
    """

    fitting_range = [10, 100]   # default frequency range for the flicker slope fitting
    plot = False   # not plotting by default

    for key, value in kwargs.iteritems():
        if key.lower() == 'fitting_range':
            if value.__len__() != 2:
                raise ValueError("The input argument f_bound should have length of 2!")
            else: 
                fitting_range = value
        elif key.lower() == 'plot':
            plot = value

    f = np.array(f_in)
    ind = np.where((f >= fitting_range[0]) & (f <= fitting_range[1]) & (f > 0))[0]  # np.where returns a tuple of np.array
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(np.log10(f[ind]), np.log10(np.array(P_in)[ind]) )
    beta = -slope
    P0 = 10**intercept / f0**beta

    if plot: 
        plt.figure(100)
        plt.loglog(f_in, P_in)
        h_line = plt.loglog(f[ind], 10**intercept / f[ind]**beta)
        plt.setp(h_line, 'linewidth', 3)
        plt.xlabel('f')
        plt.ylabel('P')
        plt.title('beta=%.3f, P0=%.3e' % (beta, P0))
        plt.legend(['Data', 'Fitted'])
        plt.show()

    return beta, P0

def zero_data(data_in, baseline_pts_ratio, option_str):
    """
    Zero the second column of an N-by-2 numpy.arragy matrix with a baseline calculated from a user 
    defined region

    Input args: 
    data_in: data to be filtered. Should be a column vector or N-by-2 matrix
    baseline_pts: the fraction of total data points the baseline is going to be calculated from 
    option_str:  either 'first' or 'last'. When option_str is 'first', the baseline is going to be 
    calculated from the first m*baseline_pts_ratio points. When option_str is 'last', the baseline 
    is going to be calculated from the last m*baseline_pts_ratio points

    Return an updated numpy.array matrix
    """
    
    # First do error checking
    if data_in.ndim ==1:
        m = len(data_in)
        n = 1
    else:
        (m, n) = data_in.shape

    if n >=3:
        raise RuntimeError('Input data should be a column vector or N-by-2 matrix')
    elif n==2:
        data = data_in[:,1]
    elif n==1:
        data = data_in

    if option_str.lower() == 'first':
        tmp = data[0:np.floor(m*baseline_pts_ratio)]
    elif option_str.lower() == 'last':
        tmp = data[np.floor(m*(1-baseline_pts_ratio)):]
    else: 
        raise RuntimeError("Invalid input option. Should be either 'first' or 'last'")

    baseline = np.sum(tmp)/len(tmp)
    if n == 1:
        y = data - baseline
    elif n == 2:
        y = np.zeros([m,n])
        y[:,0] = data_in[:,0]
        y[:,1] = data - baseline

    return y 


